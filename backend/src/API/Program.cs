using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using Serilog;
using System.Text;
using Data;
using Core.Interfaces;
using Data.Repositories;
using Core.Services;
using API.Middleware;
using Npgsql;

var builder = WebApplication.CreateBuilder(args);

// Настройка Serilog
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .WriteTo.File("logs/business-shop-.txt", rollingInterval: RollingInterval.Day)
    .CreateLogger();

builder.Host.UseSerilog();

// Добавление сервисов в контейнер
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// Настройка Swagger с JWT
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo 
    { 
        Title = "FloraStock API", 
        Version = "v1",
        Description = "API для системы управления складом цветов"
    });
    
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\"",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });
    
    c.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
});

// Настройка JWT аутентификации.
// Секреты переопределяются переменными окружения (уже подключены по умолчанию):
//   Jwt__Key, Jwt__Issuer, Jwt__Audience,
//   ConnectionStrings__DefaultConnection, Cors__AllowedOrigins__0, ...
var jwtKey = builder.Configuration["Jwt:Key"] ?? throw new InvalidOperationException("JWT Key not configured");
var jwtIssuer = builder.Configuration["Jwt:Issuer"] ?? throw new InvalidOperationException("JWT Issuer not configured");
var jwtAudience = builder.Configuration["Jwt:Audience"] ?? throw new InvalidOperationException("JWT Audience not configured");

if (jwtKey.Contains("change-in-production") || jwtKey.Length < 32)
{
    Log.Warning("Используется placeholder JWT-ключа из appsettings.json! " +
                "Для продакшена задайте переменную окружения Jwt__Key (мин. 32 символа).");
}

builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        ValidIssuer = jwtIssuer,
        ValidAudience = jwtAudience,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey))
    };
});

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy =>
        policy.RequireClaim("AccessLevel", "admin"));
    
    options.AddPolicy("ManagerOrAdmin", policy =>
        policy.RequireClaim("AccessLevel", "admin", "manager"));
});

// Настройка Entity Framework
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection") ?? 
    throw new InvalidOperationException("Connection string not configured");

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(connectionString));

// Регистрация репозиториев
builder.Services.AddScoped<ICategoryRepository, CategoryRepository>();
builder.Services.AddScoped<IProductRepository, ProductRepository>();
builder.Services.AddScoped<IClientRepository, ClientRepository>();
builder.Services.AddScoped<IEmployeeRepository, EmployeeRepository>();
builder.Services.AddScoped<ISupplierRepository, SupplierRepository>();
builder.Services.AddScoped<IOrderRepository, OrderRepository>();
builder.Services.AddScoped<IBatchRepository, BatchRepository>();
builder.Services.AddScoped<IInventoryRepository, InventoryRepository>();

// Регистрация сервисов
builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.AddScoped<IInventoryService, InventoryService>();

// Настройка CORS: разрешённые origins читаются из Cors:AllowedOrigins.
// Десктопный клиент и Swagger (same-origin) CORS не требуют,
// поэтому по умолчанию список пуст и cross-origin заблокирован.
var corsOrigins = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>()
    ?? Array.Empty<string>();
builder.Services.AddCors(options =>
{
    options.AddPolicy("ApiCors", policy =>
    {
        policy.WithOrigins(corsOrigins)
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// Инициализация базы данных
await InitializeDatabaseAsync(connectionString, app);

// Настройка pipeline обработки HTTP запросов
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

// Глобальная обработка ошибок
app.UseMiddleware<ExceptionHandlingMiddleware>();

if (corsOrigins.Length > 0)
{
    app.UseCors("ApiCors");
    Log.Information("CORS разрешён для: {Origins}", string.Join(", ", corsOrigins));
}
else
{
    Log.Information("CORS выключен (same-origin only). origins задаются через Cors:AllowedOrigins");
}

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

try
{
    Log.Information("Starting FloraStock API");
    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "Application terminated unexpectedly");
}
finally
{
    Log.CloseAndFlush();
}

async Task InitializeDatabaseAsync(string connectionString, WebApplication app)
{
    var builder_conn = new Npgsql.NpgsqlConnectionStringBuilder(connectionString);
    var dbName = builder_conn.Database;
    
    // Проверяем, существует ли база данных
    bool dbExists = false;
    
    try
    {
        Log.Information("Проверка подключения к PostgreSQL...");
        
        // Подключаемся к postgres базе для проверки/создания
        builder_conn.Database = "postgres";
        using (var conn = new Npgsql.NpgsqlConnection(builder_conn.ToString()))
        {
            await conn.OpenAsync();
            
            using var cmd = new Npgsql.NpgsqlCommand("SELECT 1 FROM pg_database WHERE datname = @db", conn);
            cmd.Parameters.AddWithValue("@db", dbName ?? "");
            var exists = await cmd.ExecuteScalarAsync();
            dbExists = exists != null;
            
            if (!dbExists)
            {
                Log.Information("Создание базы данных {DbName}...", dbName);
                if (!System.Text.RegularExpressions.Regex.IsMatch(dbName ?? "", "^[A-Za-z_][A-Za-z0-9_]*$"))
                    throw new InvalidOperationException("Недопустимое имя базы данных");
                using var createCmd = new Npgsql.NpgsqlCommand($"CREATE DATABASE \"{dbName}\"", conn);
                await createCmd.ExecuteNonQueryAsync();
                Log.Information("База данных {DbName} создана", dbName);
                dbExists = true;
            }
            else
            {
                Log.Information("База данных {DbName} уже существует", dbName);
            }
        }
    }
    catch (Exception ex)
    {
        Log.Error(ex, "Ошибка при проверке/создании базы данных: {Error}", ex.Message);
        return;
    }
    
    // Создаем таблицы и заполняем данными
    if (dbExists)
    {
        try
        {
            using var scope = app.Services.CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            
            // Создаем таблицы
            context.Database.EnsureCreated();
            Log.Information("Таблицы базы данных созданы");

            // Нормализация учётных данных БД, созданных до введения колонки login/хешей
            await NormalizeEmployeeCredentialsAsync(context);
            
            // Проверяем, есть ли данные (проверяем по заказам)
            var orderCount = context.Order.Count();
            
            if (orderCount == 0)
            {
                Log.Information("Заполнение базы данных тестовыми данными...");
                
                // Категории
                var categories = new[]
                {
                    new Shared.Entities.Category { Name = "Розы", Description = "Классические розы различных сортов и цветов" },
                    new Shared.Entities.Category { Name = "Тюльпаны", Description = "Весенние тюльпаны голландской селекции" },
                    new Shared.Entities.Category { Name = "Хризантемы", Description = "Многолетние цветы, популярные в букетах" },
                    new Shared.Entities.Category { Name = "Герберы", Description = "Крупные яркие цветы, похожие на ромашки" },
                    new Shared.Entities.Category { Name = "Орхидеи", Description = "Экзотические тропические цветы" },
                    new Shared.Entities.Category { Name = "Лилии", Description = "Цветы с сильным ароматом и крупными бутонами" },
                    new Shared.Entities.Category { Name = "Пионы", Description = "Пышные цветы, популярные в свадебных букетах" },
                    new Shared.Entities.Category { Name = "Ирисы", Description = "Нежные весенние цветы с оригинальной формой" },
                    new Shared.Entities.Category { Name = "Гвоздики", Description = "Классические цветы для различных мероприятий" },
                    new Shared.Entities.Category { Name = "Экзотические цветы", Description = "Редкие и необычные цветы из тропиков" }
                };
                context.Category.AddRange(categories);
                await context.SaveChangesAsync();
                
                // Сотрудники (пароли хранятся хешами, вход — по полю Login)
                var employees = new[]
                {
                    new Shared.Entities.Employee { FullName = "Администратор", Position = "Системный администратор", PhoneNumber = "+79999999999", Email = "admin@florastock.ru", Login = "admin", LoginPassword = Core.Services.PasswordHasher.Hash("admin"), AccessLevel = "admin" },
                    new Shared.Entities.Employee { FullName = "Иванова Анна Петровна", Position = "Флорист", PhoneNumber = "+79161234567", Email = "ivanova@flowerstore.ru", Login = "ivanova", LoginPassword = Core.Services.PasswordHasher.Hash("ivanova123"), AccessLevel = "florist" },
                    new Shared.Entities.Employee { FullName = "Петров Сергей Иванович", Position = "Менеджер по закупкам", PhoneNumber = "+79162345678", Email = "petrov@flowerstore.ru", Login = "petrov", LoginPassword = Core.Services.PasswordHasher.Hash("petrov456"), AccessLevel = "purchasing" },
                    new Shared.Entities.Employee { FullName = "Сидорова Елена Владимировна", Position = "Продавец-консультант", PhoneNumber = "+79163456789", Email = "sidorova@flowerstore.ru", Login = "sidorova", LoginPassword = Core.Services.PasswordHasher.Hash("sidorova789"), AccessLevel = "seller" },
                    new Shared.Entities.Employee { FullName = "Кузнецов Алексей Дмитриевич", Position = "Курьер", PhoneNumber = "+79164567890", Email = "kuznetsov@flowerstore.ru", Login = "kuznetsov", LoginPassword = Core.Services.PasswordHasher.Hash("kuznetsov000"), AccessLevel = "courier" },
                    new Shared.Entities.Employee { FullName = "Смирнова Ольга Александровна", Position = "Флорист", PhoneNumber = "+79165678901", Email = "smirnova@flowerstore.ru", Login = "smirnova", LoginPassword = Core.Services.PasswordHasher.Hash("smirnova111"), AccessLevel = "florist" },
                    new Shared.Entities.Employee { FullName = "Васильев Дмитрий Игоревич", Position = "Складской работник", PhoneNumber = "+79166789012", Email = "vasiliev@flowerstore.ru", Login = "vasiliev", LoginPassword = Core.Services.PasswordHasher.Hash("vasiliev222"), AccessLevel = "warehouse" },
                    new Shared.Entities.Employee { FullName = "Николаева Татьяна Сергеевна", Position = "Администратор", PhoneNumber = "+79167890123", Email = "nikolaeva@flowerstore.ru", Login = "nikolaeva", LoginPassword = Core.Services.PasswordHasher.Hash("nikolaeva333"), AccessLevel = "admin" },
                    new Shared.Entities.Employee { FullName = "Андреев Андрей Андреевич", Position = "Директор", PhoneNumber = "+79168901234", Email = "andreev@flowerstore.ru", Login = "andreev", LoginPassword = Core.Services.PasswordHasher.Hash("andreev444"), AccessLevel = "admin" },
                    new Shared.Entities.Employee { FullName = "Макарова Ирина Викторовна", Position = "Флорист", PhoneNumber = "+79169012345", Email = "makarova@flowerstore.ru", Login = "makarova", LoginPassword = Core.Services.PasswordHasher.Hash("makarova555"), AccessLevel = "florist" }
                };
                context.Employee.AddRange(employees);
                await context.SaveChangesAsync();
                
                // Клиенты
                var clients = new[]
                {
                    new Shared.Entities.Client { FullName = "Соколова Мария Ивановна", PhoneNumber = "+79031112233", Email = "sokolova@mail.ru" },
                    new Shared.Entities.Client { FullName = "Волков Андрей Петрович", PhoneNumber = "+79032223344", Email = "volkov@mail.ru" },
                    new Shared.Entities.Client { FullName = "Белова Екатерина Сергеевна", PhoneNumber = "+79033334455", Email = "belova@mail.ru" },
                    new Shared.Entities.Client { FullName = "Козлов Дмитрий Владимирович", PhoneNumber = "+79034445566", Email = "kozlov@mail.ru" },
                    new Shared.Entities.Client { FullName = "Новикова Ирина Дмитриевна", PhoneNumber = "+79035556677", Email = "novikova@mail.ru" },
                    new Shared.Entities.Client { FullName = "Морозов Виктор Алексеевич", PhoneNumber = "+79036667788", Email = "morozov@mail.ru" },
                    new Shared.Entities.Client { FullName = "Павлова Наталья Николаевна", PhoneNumber = "+79037778899", Email = "pavlova@mail.ru" },
                    new Shared.Entities.Client { FullName = "Семенов Борис Борисович", PhoneNumber = "+79038889900", Email = "semenov@mail.ru" },
                    new Shared.Entities.Client { FullName = "Григорьева Людмила Олеговна", PhoneNumber = "+79039990011", Email = "grigoreva@mail.ru" },
                    new Shared.Entities.Client { FullName = "Орлов Станислав Иванович", PhoneNumber = "+79030001122", Email = "orlov@mail.ru" }
                };
                context.Client.AddRange(clients);
                await context.SaveChangesAsync();
                
                // Поставщики
                var suppliers = new[]
                {
                    new Shared.Entities.Supplier { Name = "ООО Голландские розы", PhoneNumber = "+74951234567", Email = "info@dutchroses.ru", Details = "ИНН 7701123456", Address = "Москва, ул. Цветочная, д. 1" },
                    new Shared.Entities.Supplier { Name = "АО Тюльпаны из Голландии", PhoneNumber = "+74952223344", Email = "sales@tulips.ru", Details = "ИНН 7711234567", Address = "Москва, пр. Садовый, д. 25" },
                    new Shared.Entities.Supplier { Name = "ЗАО Эквадорские розы", PhoneNumber = "+74953334455", Email = "order@ecuadorroses.ru", Details = "ИНН 7721345678", Address = "Санкт-Петербург, Невский пр., д. 45" },
                    new Shared.Entities.Supplier { Name = "ООО Кенийские цветы", PhoneNumber = "+74954445566", Email = "info@kenyaflowers.ru", Details = "ИНН 7731456789", Address = "Москва, ул. Африканская, д. 10" },
                    new Shared.Entities.Supplier { Name = "ИП Орхидеи Азии", PhoneNumber = "+74955556677", Email = "orchids@asia.ru", Details = "ИНН 7741567890", Address = "Казань, ул. Восточная, д. 15" },
                    new Shared.Entities.Supplier { Name = "ООО Российские цветы", PhoneNumber = "+74956667788", Email = "flowers@russianflowers.ru", Details = "ИНН 7751678901", Address = "Москва, ул. Полевая, д. 20" },
                    new Shared.Entities.Supplier { Name = "АО Пионы из Китая", PhoneNumber = "+74957778899", Email = "peonies@china.ru", Details = "ИНН 7761789012", Address = "Екатеринбург, ул. Китайская, д. 30" },
                    new Shared.Entities.Supplier { Name = "ООО Лилии Урала", PhoneNumber = "+74958889900", Email = "lilies@ural.ru", Details = "ИНН 7771890123", Address = "Новосибирск, Красный пр., д. 50" },
                    new Shared.Entities.Supplier { Name = "ЗАО Герберы Европы", PhoneNumber = "+74959990011", Email = "gerbera@europe.ru", Details = "ИНН 7781901234", Address = "Москва, ш. Европейское, д. 12" },
                    new Shared.Entities.Supplier { Name = "ООО Экзотика мира", PhoneNumber = "+74950001122", Email = "exotic@world.ru", Details = "ИНН 7791012345", Address = "Ростов-на-Дону, ул. Экзотическая, д. 70" }
                };
                context.Supplier.AddRange(suppliers);
                await context.SaveChangesAsync();
                
                // Товары
                var products = new[]
                {
                    new Shared.Entities.Product { CategoryID = 1, Name = "Роза Гран При", Description = "Классическая красная роза премиум качества", Unit = "шт", PurchasePrice = 150, RetailPrice = 300, ShelfLifeDays = 10, Color = "Красный", StemLengthCm = 70 },
                    new Shared.Entities.Product { CategoryID = 1, Name = "Роза Аваланж", Description = "Белая роза голландской селекции", Unit = "шт", PurchasePrice = 120, RetailPrice = 250, ShelfLifeDays = 10, Color = "Белый", StemLengthCm = 60 },
                    new Shared.Entities.Product { CategoryID = 2, Name = "Тюльпан Монте Карло", Description = "Махровый желтый тюльпан", Unit = "шт", PurchasePrice = 50, RetailPrice = 100, ShelfLifeDays = 7, Color = "Желтый", StemLengthCm = 40 },
                    new Shared.Entities.Product { CategoryID = 2, Name = "Тюльпан Апельдорн", Description = "Классический красный тюльпан", Unit = "шт", PurchasePrice = 45, RetailPrice = 90, ShelfLifeDays = 7, Color = "Красный", StemLengthCm = 45 },
                    new Shared.Entities.Product { CategoryID = 3, Name = "Хризантема Сантини", Description = "Мелкоцветковая кустовая хризантема", Unit = "шт", PurchasePrice = 70, RetailPrice = 140, ShelfLifeDays = 14, Color = "Белый", StemLengthCm = 50 },
                    new Shared.Entities.Product { CategoryID = 3, Name = "Хризантема одноголовая", Description = "Крупная хризантема для букетов", Unit = "шт", PurchasePrice = 80, RetailPrice = 160, ShelfLifeDays = 14, Color = "Желтый", StemLengthCm = 60 },
                    new Shared.Entities.Product { CategoryID = 4, Name = "Гербера Джемсона", Description = "Крупная яркая гербера", Unit = "шт", PurchasePrice = 65, RetailPrice = 130, ShelfLifeDays = 12, Color = "Оранжевый", StemLengthCm = 55 },
                    new Shared.Entities.Product { CategoryID = 4, Name = "Гербера мини", Description = "Мелкая гербера для композиций", Unit = "шт", PurchasePrice = 55, RetailPrice = 110, ShelfLifeDays = 12, Color = "Розовый", StemLengthCm = 40 },
                    new Shared.Entities.Product { CategoryID = 5, Name = "Фаленопсис белый", Description = "Орхидея фаленопсис в горшке", Unit = "шт", PurchasePrice = 500, RetailPrice = 1200, ShelfLifeDays = 30, Color = "Белый" },
                    new Shared.Entities.Product { CategoryID = 5, Name = "Дендробиум", Description = "Экзотическая орхидея дендробиум", Unit = "шт", PurchasePrice = 450, RetailPrice = 1000, ShelfLifeDays = 30, Color = "Фиолетовый" }
                };
                context.Product.AddRange(products);
                await context.SaveChangesAsync();
                
                // Партии
                var batches = new[]
                {
                    new Shared.Entities.Batch { SupplierID = 1, DeliveryDate = new DateTime(2024, 01, 15, 0, 0, 0, DateTimeKind.Utc), InvoiceNumber = "РОЗ-001/2024", Quantity = 500, CostPrice = 75000 },
                    new Shared.Entities.Batch { SupplierID = 2, DeliveryDate = new DateTime(2024, 01, 20, 0, 0, 0, DateTimeKind.Utc), InvoiceNumber = "ТЮЛ-002/2024", Quantity = 1000, CostPrice = 50000 },
                    new Shared.Entities.Batch { SupplierID = 3, DeliveryDate = new DateTime(2024, 01, 25, 0, 0, 0, DateTimeKind.Utc), InvoiceNumber = "ЭКВ-003/2024", Quantity = 300, CostPrice = 45000 },
                    new Shared.Entities.Batch { SupplierID = 4, DeliveryDate = new DateTime(2024, 02, 01, 0, 0, 0, DateTimeKind.Utc), InvoiceNumber = "КЕН-004/2024", Quantity = 400, CostPrice = 28000 },
                    new Shared.Entities.Batch { SupplierID = 5, DeliveryDate = new DateTime(2024, 02, 05, 0, 0, 0, DateTimeKind.Utc), InvoiceNumber = "ОРХ-005/2024", Quantity = 50, CostPrice = 25000 },
                    new Shared.Entities.Batch { SupplierID = 6, DeliveryDate = new DateTime(2024, 02, 10, 0, 0, 0, DateTimeKind.Utc), InvoiceNumber = "РОС-006/2024", Quantity = 600, CostPrice = 48000 },
                    new Shared.Entities.Batch { SupplierID = 7, DeliveryDate = new DateTime(2024, 02, 15, 0, 0, 0, DateTimeKind.Utc), InvoiceNumber = "ПИО-007/2024", Quantity = 200, CostPrice = 16000 },
                    new Shared.Entities.Batch { SupplierID = 8, DeliveryDate = new DateTime(2024, 02, 20, 0, 0, 0, DateTimeKind.Utc), InvoiceNumber = "ЛИЛ-008/2024", Quantity = 350, CostPrice = 24500 },
                    new Shared.Entities.Batch { SupplierID = 9, DeliveryDate = new DateTime(2024, 02, 25, 0, 0, 0, DateTimeKind.Utc), InvoiceNumber = "ГЕР-009/2024", Quantity = 450, CostPrice = 29250 },
                    new Shared.Entities.Batch { SupplierID = 10, DeliveryDate = new DateTime(2024, 03, 01, 0, 0, 0, DateTimeKind.Utc), InvoiceNumber = "ЭКЗ-010/2024", Quantity = 150, CostPrice = 22500 }
                };
                context.Batch.AddRange(batches);
                await context.SaveChangesAsync();
                
                // Заказы
                var orders = new[]
                {
                    new Shared.Entities.Order { ClientID = 1, EmployeeID = 1, ProductID = 1, OrderDate = new DateTime(2024, 01, 20, 0, 0, 0, DateTimeKind.Utc), Status = "Доставлен", OrderNumber = "ORD-001/2024", TotalAmount = 1500 },
                    new Shared.Entities.Order { ClientID = 2, EmployeeID = 3, ProductID = 3, OrderDate = new DateTime(2024, 01, 22, 0, 0, 0, DateTimeKind.Utc), Status = "Выполнен", OrderNumber = "ORD-002/2024", TotalAmount = 500 },
                    new Shared.Entities.Order { ClientID = 3, EmployeeID = 1, ProductID = 5, OrderDate = new DateTime(2024, 01, 25, 0, 0, 0, DateTimeKind.Utc), Status = "Доставлен", OrderNumber = "ORD-003/2024", TotalAmount = 1120 },
                    new Shared.Entities.Order { ClientID = 4, EmployeeID = 5, ProductID = 2, OrderDate = new DateTime(2024, 01, 28, 0, 0, 0, DateTimeKind.Utc), Status = "В обработке", OrderNumber = "ORD-004/2024", TotalAmount = 1250 },
                    new Shared.Entities.Order { ClientID = 5, EmployeeID = 3, ProductID = 7, OrderDate = new DateTime(2024, 02, 01, 0, 0, 0, DateTimeKind.Utc), Status = "Выполнен", OrderNumber = "ORD-005/2024", TotalAmount = 780 },
                    new Shared.Entities.Order { ClientID = 6, EmployeeID = 1, ProductID = 4, OrderDate = new DateTime(2024, 02, 05, 0, 0, 0, DateTimeKind.Utc), Status = "Доставлен", OrderNumber = "ORD-006/2024", TotalAmount = 720 },
                    new Shared.Entities.Order { ClientID = 7, EmployeeID = 5, ProductID = 6, OrderDate = new DateTime(2024, 02, 10, 0, 0, 0, DateTimeKind.Utc), Status = "В обработке", OrderNumber = "ORD-007/2024", TotalAmount = 960 },
                    new Shared.Entities.Order { ClientID = 8, EmployeeID = 3, ProductID = 8, OrderDate = new DateTime(2024, 02, 15, 0, 0, 0, DateTimeKind.Utc), Status = "Выполнен", OrderNumber = "ORD-008/2024", TotalAmount = 660 },
                    new Shared.Entities.Order { ClientID = 9, EmployeeID = 1, ProductID = 9, OrderDate = new DateTime(2024, 02, 20, 0, 0, 0, DateTimeKind.Utc), Status = "Доставлен", OrderNumber = "ORD-009/2024", TotalAmount = 2400 },
                    new Shared.Entities.Order { ClientID = 10, EmployeeID = 5, ProductID = 10, OrderDate = new DateTime(2024, 02, 25, 0, 0, 0, DateTimeKind.Utc), Status = "В обработке", OrderNumber = "ORD-010/2024", TotalAmount = 2000 }
                };
                context.Order.AddRange(orders);
                await context.SaveChangesAsync();
                
                // Позиции заказов
                var orderPositions = new[]
                {
                    new Shared.Entities.OrderPosition { OrderID = 1, ProductID = 1, Quantity = 5, UnitPrice = 300 },
                    new Shared.Entities.OrderPosition { OrderID = 1, ProductID = 2, Quantity = 3, UnitPrice = 250 },
                    new Shared.Entities.OrderPosition { OrderID = 2, ProductID = 3, Quantity = 5, UnitPrice = 100 },
                    new Shared.Entities.OrderPosition { OrderID = 3, ProductID = 5, Quantity = 8, UnitPrice = 140 },
                    new Shared.Entities.OrderPosition { OrderID = 4, ProductID = 2, Quantity = 5, UnitPrice = 250 },
                    new Shared.Entities.OrderPosition { OrderID = 5, ProductID = 7, Quantity = 6, UnitPrice = 130 },
                    new Shared.Entities.OrderPosition { OrderID = 6, ProductID = 4, Quantity = 8, UnitPrice = 90 },
                    new Shared.Entities.OrderPosition { OrderID = 7, ProductID = 6, Quantity = 6, UnitPrice = 160 },
                    new Shared.Entities.OrderPosition { OrderID = 8, ProductID = 8, Quantity = 6, UnitPrice = 110 },
                    new Shared.Entities.OrderPosition { OrderID = 9, ProductID = 9, Quantity = 2, UnitPrice = 1200 }
                };
                context.OrderPosition.AddRange(orderPositions);
                await context.SaveChangesAsync();
                
                // Складские позиции
                var inventory = new[]
                {
                    new Shared.Entities.Inventory { ProductID = 1, BatchID = 1, Quantity = 100, ReceiptDate = new DateTime(2024, 01, 15, 0, 0, 0, DateTimeKind.Utc), StorageLocation = "Холодильник А1", StorageTemperature = "+2°C", HumidityLevel = "85%" },
                    new Shared.Entities.Inventory { ProductID = 2, BatchID = 1, Quantity = 80, ReceiptDate = new DateTime(2024, 01, 15, 0, 0, 0, DateTimeKind.Utc), StorageLocation = "Холодильник А2", StorageTemperature = "+2°C", HumidityLevel = "85%" },
                    new Shared.Entities.Inventory { ProductID = 3, BatchID = 2, Quantity = 200, ReceiptDate = new DateTime(2024, 01, 20, 0, 0, 0, DateTimeKind.Utc), StorageLocation = "Холодильник Б1", StorageTemperature = "+4°C", HumidityLevel = "80%" },
                    new Shared.Entities.Inventory { ProductID = 4, BatchID = 2, Quantity = 150, ReceiptDate = new DateTime(2024, 01, 20, 0, 0, 0, DateTimeKind.Utc), StorageLocation = "Холодильник Б2", StorageTemperature = "+4°C", HumidityLevel = "80%" },
                    new Shared.Entities.Inventory { ProductID = 5, BatchID = 4, Quantity = 120, ReceiptDate = new DateTime(2024, 02, 01, 0, 0, 0, DateTimeKind.Utc), StorageLocation = "Холодильник В1", StorageTemperature = "+3°C", HumidityLevel = "75%" },
                    new Shared.Entities.Inventory { ProductID = 6, BatchID = 6, Quantity = 100, ReceiptDate = new DateTime(2024, 02, 10, 0, 0, 0, DateTimeKind.Utc), StorageLocation = "Холодильник В2", StorageTemperature = "+3°C", HumidityLevel = "75%" },
                    new Shared.Entities.Inventory { ProductID = 7, BatchID = 9, Quantity = 90, ReceiptDate = new DateTime(2024, 02, 25, 0, 0, 0, DateTimeKind.Utc), StorageLocation = "Холодильник Г1", StorageTemperature = "+5°C", HumidityLevel = "70%" },
                    new Shared.Entities.Inventory { ProductID = 8, BatchID = 9, Quantity = 80, ReceiptDate = new DateTime(2024, 02, 25, 0, 0, 0, DateTimeKind.Utc), StorageLocation = "Холодильник Г2", StorageTemperature = "+5°C", HumidityLevel = "70%" },
                    new Shared.Entities.Inventory { ProductID = 9, BatchID = 5, Quantity = 15, ReceiptDate = new DateTime(2024, 02, 05, 0, 0, 0, DateTimeKind.Utc), StorageLocation = "Теплица 1", StorageTemperature = "+18°C", HumidityLevel = "60%" },
                    new Shared.Entities.Inventory { ProductID = 10, BatchID = 10, Quantity = 25, ReceiptDate = new DateTime(2024, 03, 01, 0, 0, 0, DateTimeKind.Utc), StorageLocation = "Теплица 2", StorageTemperature = "+20°C", HumidityLevel = "65%" }
                };
                context.Inventory.AddRange(inventory);
                await context.SaveChangesAsync();
                
                // OrderItem (дублирует OrderPosition)
                var orderItems = new[]
                {
                    new Shared.Entities.OrderItem { OrderID = 1, ProductID = 1, Quantity = 5, UnitPrice = 300 },
                    new Shared.Entities.OrderItem { OrderID = 1, ProductID = 2, Quantity = 3, UnitPrice = 250 },
                    new Shared.Entities.OrderItem { OrderID = 2, ProductID = 3, Quantity = 5, UnitPrice = 100 },
                    new Shared.Entities.OrderItem { OrderID = 3, ProductID = 5, Quantity = 8, UnitPrice = 140 },
                    new Shared.Entities.OrderItem { OrderID = 4, ProductID = 2, Quantity = 5, UnitPrice = 250 },
                    new Shared.Entities.OrderItem { OrderID = 5, ProductID = 7, Quantity = 6, UnitPrice = 130 },
                    new Shared.Entities.OrderItem { OrderID = 6, ProductID = 4, Quantity = 8, UnitPrice = 90 },
                    new Shared.Entities.OrderItem { OrderID = 7, ProductID = 6, Quantity = 6, UnitPrice = 160 },
                    new Shared.Entities.OrderItem { OrderID = 8, ProductID = 8, Quantity = 6, UnitPrice = 110 },
                    new Shared.Entities.OrderItem { OrderID = 9, ProductID = 9, Quantity = 2, UnitPrice = 1200 }
                };
                context.OrderItem.AddRange(orderItems);
                await context.SaveChangesAsync();
                
                Log.Information("База данных FloraStock заполнена тестовыми данными");
            }
            else
            {
                Log.Information("Данные уже существуют в базе");
            }
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Ошибка создания таблиц: {Error}", ex.Message);
        }
    }

    async Task NormalizeEmployeeCredentialsAsync(Data.AppDbContext context)
    {
        // Одноразовая миграция старых БД:
        // - колонка login (см. docs/sql/08_auth_login.sql),
        // - SHA256-хеши вместо plaintext-паролей.
        // Идемпотентна, для новых БД ничего не меняет.
        try
        {
            var hasLoginColumn = await context.Database.SqlQueryRaw<int>(
                "SELECT COUNT(*) AS \"Value\" FROM information_schema.columns " +
                "WHERE table_name = 'employee' AND column_name = 'login'").FirstOrDefaultAsync();
            if (hasLoginColumn == 0)
            {
                Log.Warning("В таблице employee нет колонки login — выполните docs/sql/08_auth_login.sql, нормализация пропущена");
                return;
            }

            var employees = await context.Employee.ToListAsync();
            var usedLogins = new HashSet<string>(
                employees.Where(e => !string.IsNullOrWhiteSpace(e.Login))
                         .Select(e => e.Login!.Trim().ToLowerInvariant()));
            var changed = 0;

            foreach (var e in employees)
            {
                if (string.IsNullOrWhiteSpace(e.Login))
                {
                    var baseLogin = (e.Email?.Split('@')[0] ?? "").Trim().ToLowerInvariant();
                    if (string.IsNullOrEmpty(baseLogin))
                        baseLogin = $"user{e.ID}";
                    var candidate = baseLogin;
                    var suffix = 1;
                    while (usedLogins.Contains(candidate))
                        candidate = $"{baseLogin}{suffix++}";
                    e.Login = candidate;
                    usedLogins.Add(candidate);
                    changed++;
                }

                if (!string.IsNullOrEmpty(e.LoginPassword) &&
                    !Core.Services.PasswordHasher.LooksHashed(e.LoginPassword))
                {
                    e.LoginPassword = Core.Services.PasswordHasher.Hash(e.LoginPassword);
                    changed++;
                }
            }

            if (changed > 0)
            {
                await context.SaveChangesAsync();
                Log.Information("Нормализация учётных данных: обновлено записей: {Count}", changed);
            }
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Ошибка нормализации учётных данных: {Error}", ex.Message);
        }
    }
}