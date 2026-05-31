-- ==========================================
-- Инициализация базы данных "ScladSimple" с совместимыми именами таблиц
-- Бизнес - СУБД (версия совместимая с существующими DbSet)
-- ==========================================

-- Удаление существующих таблиц
DROP TABLE IF EXISTS StockPosition CASCADE;
DROP TABLE IF EXISTS OrderPosition CASCADE;
DROP TABLE IF EXISTS "Order" CASCADE;
DROP TABLE IF EXISTS Batch CASCADE;
DROP TABLE IF EXISTS Product CASCADE;
DROP TABLE IF EXISTS Client CASCADE;
DROP TABLE IF EXISTS Employee CASCADE;
DROP TABLE IF EXISTS Supplier CASCADE;
DROP TABLE IF EXISTS Category CASCADE;
DROP TABLE IF EXISTS Inventory CASCADE;
DROP TABLE IF EXISTS OrderItem CASCADE;

-- ==========================================
-- Создание таблиц с совместимыми именами
-- ==========================================

-- 1. Категории товаров
CREATE TABLE Category (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Description TEXT
);

-- 2. Сотрудники
CREATE TABLE Employee (
    ID SERIAL PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    Position VARCHAR(100),
    PhoneNumber VARCHAR(20),
    Email VARCHAR(255),
    LoginPassword VARCHAR(255),
    AccessLevel VARCHAR(50)
);

-- 3. Клиенты
CREATE TABLE Client (
    ID SERIAL PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    PhoneNumber VARCHAR(20),
    Email VARCHAR(255)
);

-- 4. Поставщики
CREATE TABLE Supplier (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    PhoneNumber VARCHAR(20),
    Email VARCHAR(255),
    Details TEXT,
    Address TEXT
);

-- 5. Товары (Цветы)
CREATE TABLE Product (
    ID SERIAL PRIMARY KEY,
    CategoryID INTEGER REFERENCES Category(ID),
    Name VARCHAR(255) NOT NULL,
    Description TEXT,
    Unit VARCHAR(50),
    PurchasePrice DECIMAL(10,2),
    RetailPrice DECIMAL(10,2),
    ShelfLifeDays INTEGER,
    Color VARCHAR(50),
    StemLengthCm INTEGER
);

-- 6. Партии поставок
CREATE TABLE Batch (
    ID SERIAL PRIMARY KEY,
    SupplierID INTEGER REFERENCES Supplier(ID),
    DeliveryDate DATE,
    InvoiceNumber VARCHAR(100),
    Quantity INTEGER,
    CostPrice DECIMAL(10,2)
);

-- 7. Заказы
CREATE TABLE "Order" (
    ID SERIAL PRIMARY KEY,
    ClientID INTEGER REFERENCES Client(ID),
    EmployeeID INTEGER REFERENCES Employee(ID),
    ProductID INTEGER REFERENCES Product(ID),
    OrderDate DATE NOT NULL,
    Status VARCHAR(50),
    OrderNumber VARCHAR(100) UNIQUE,
    TotalAmount DECIMAL(10,2)
);

-- 8. Позиции заказов
CREATE TABLE OrderPosition (
    ID SERIAL PRIMARY KEY,
    OrderID INTEGER REFERENCES "Order"(ID),
    ProductID INTEGER REFERENCES Product(ID),
    Quantity INTEGER NOT NULL,
    UnitPrice DECIMAL(10,2)
);

-- 9. Складские позиции
CREATE TABLE StockPosition (
    ID SERIAL PRIMARY KEY,
    ProductID INTEGER REFERENCES Product(ID),
    BatchID INTEGER REFERENCES Batch(ID),
    Quantity INTEGER NOT NULL,
    ReceiptDate DATE,
    StorageLocation VARCHAR(255),
    StorageTemperature VARCHAR(50),
    HumidityLevel VARCHAR(50)
);

-- 10. Таблицы для обратной совместимости
CREATE TABLE Inventory (
    ID SERIAL PRIMARY KEY,
    ProductID INTEGER REFERENCES Product(ID),
    BatchID INTEGER REFERENCES Batch(ID),
    Quantity INTEGER NOT NULL,
    ReceiptDate DATE,
    StorageLocation VARCHAR(255),
    StorageTemperature VARCHAR(50),
    HumidityLevel VARCHAR(50)
);

CREATE TABLE OrderItem (
    ID SERIAL PRIMARY KEY,
    OrderID INTEGER REFERENCES "Order"(ID),
    ProductID INTEGER REFERENCES Product(ID),
    Quantity INTEGER NOT NULL,
    UnitPrice DECIMAL(10,2)
);

-- ==========================================
-- Заполнение таблиц тестовыми данными
-- ==========================================

-- 1. Категории цветов
INSERT INTO Category (Name, Description) VALUES
('Розы', 'Классические розы различных сортов и цветов'),
('Тюльпаны', 'Весенние тюльпаны голландской селекции'),
('Хризантемы', 'Многолетние цветы, популярные в букетах'),
('Герберы', 'Крупные яркие цветы, похожие на ромашки'),
('Орхидеи', 'Экзотические тропические цветы'),
('Лилии', 'Цветы с сильным ароматом и крупными бутонами'),
('Пионы', 'Пышные цветы, популярные в свадебных букетах'),
('Ирисы', 'Нежные весенние цветы с оригинальной формой'),
('Гвоздики', 'Классические цветы для различных мероприятий'),
('Экзотические цветы', 'Редкие и необычные цветы из тропиков');

-- 2. Сотрудники (admin user: login=admin, password=admin)
INSERT INTO Employee (FullName, Position, PhoneNumber, Email, LoginPassword, AccessLevel) VALUES
('Администратор', 'Системный администратор', '+79999999999', 'admin@businessshop.ru', 'admin', 'admin');
('Иванова Анна Петровна', 'Флорист', '+79161234567', 'ivanova@flowerstore.ru', 'ivanova123', 'florist'),
('Петров Сергей Иванович', 'Менеджер по закупкам', '+79162345678', 'petrov@flowerstore.ru', 'petrov456', 'purchasing'),
('Сидорова Елена Владимировна', 'Продавец-консультант', '+79163456789', 'sidorova@flowerstore.ru', 'sidorova789', 'seller'),
('Кузнецов Алексей Дмитриевич', 'Курьер', '+79164567890', 'kuznetsov@flowerstore.ru', 'kuznetsov000', 'courier'),
('Смирнова Ольга Александровна', 'Флорист', '+79165678901', 'smirnova@flowerstore.ru', 'smirnova111', 'florist'),
('Васильев Дмитрий Игоревич', 'Складской работник', '+79166789012', 'vasiliev@flowerstore.ru', 'vasiliev222', 'warehouse'),
('Николаева Татьяна Сергеевна', 'Администратор', '+79167890123', 'nikolaeva@flowerstore.ru', 'nikolaeva333', 'admin'),
('Андреев Андрей Андреевич', 'Директор', '+79168901234', 'andreev@flowerstore.ru', 'andreev444', 'admin'),
('Макарова Ирина Викторовна', 'Флорист', '+79169012345', 'makarova@flowerstore.ru', 'makarova555', 'florist'),
('Федоров Сергей Александрович', 'Водитель-экспедитор', '+79160123456', 'fedorov@flowerstore.ru', 'fedorov666', 'courier');

-- 3. Клиенты
INSERT INTO Client (FullName, PhoneNumber, Email) VALUES
('Соколова Мария Ивановна', '+79031112233', 'sokolova@mail.ru'),
('Волков Андрей Петрович', '+79032223344', 'volkov@mail.ru'),
('Белова Екатерина Сергеевна', '+79033334455', 'belova@mail.ru'),
('Козлов Дмитрий Владимирович', '+79034445566', 'kozlov@mail.ru'),
('Новикова Ирина Дмитриевна', '+79035556677', 'novikova@mail.ru'),
('Морозов Виктор Алексеевич', '+79036667788', 'morozov@mail.ru'),
('Павлова Наталья Николаевна', '+79037778899', 'pavlova@mail.ru'),
('Семенов Борис Борисович', '+79038889900', 'semenov@mail.ru'),
('Григорьева Людмила Олеговна', '+79039990011', 'grigoreva@mail.ru'),
('Орлов Станислав Иванович', '+79030001122', 'orlov@mail.ru');

-- 4. Поставщики цветов
INSERT INTO Supplier (Name, PhoneNumber, Email, Details, Address) VALUES
('ООО "Голландские розы"', '+74951234567', 'info@dutchroses.ru', 'ИНН 7701123456, КПП 770101001', 'Москва, ул. Цветочная, д. 1'),
('АО "Тюльпаны из Голландии"', '+74952223344', 'sales@tulips.ru', 'ИНН 7711234567, КПП 771101001', 'Москва, пр. Садовый, д. 25'),
('ЗАО "Эквадорские розы"', '+74953334455', 'order@ecuadorroses.ru', 'ИНН 7721345678, КПП 772101001', 'Санкт-Петербург, Невский пр., д. 45'),
('ООО "Кенийские цветы"', '+74954445566', 'info@kenyaflowers.ru', 'ИНН 7731456789, КПП 773101001', 'Москва, ул. Африканская, д. 10'),
('ИП "Орхидеи Азии"', '+74955556677', 'orchids@asia.ru', 'ИНН 7741567890, КПП 774101001', 'Казань, ул. Восточная, д. 15'),
('ООО "Российские цветы"', '+74956667788', 'flowers@russianflowers.ru', 'ИНН 7751678901, КПП 775101001', 'Москва, ул. Полевая, д. 20'),
('АО "Пионы из Китая"', '+74957778899', 'peonies@china.ru', 'ИНН 7761789012, КПП 776101001', 'Екатеринбург, ул. Китайская, д. 30'),
('ООО "Лилии Урала"', '+74958889900', 'lilies@ural.ru', 'ИНН 7771890123, КПП 777101001', 'Новосибирск, Красный пр., д. 50'),
('ЗАО "Герберы Европы"', '+74959990011', 'gerbera@europe.ru', 'ИНН 7781901234, КПП 778101001', 'Москва, ш. Европейское, д. 12'),
('ООО "Экзотика мира"', '+74950001122', 'exotic@world.ru', 'ИНН 7791012345, КПП 779101001', 'Ростов-на-Дону, ул. Экзотическая, д. 70');

-- 5. Товары (Цветы)
INSERT INTO Product (CategoryID, Name, Description, Unit, PurchasePrice, RetailPrice, ShelfLifeDays, Color, StemLengthCm) VALUES
(1, 'Роза Гран При', 'Классическая красная роза премиум качества', 'шт', 150.00, 300.00, 10, 'Красный', 70),
(1, 'Роза Аваланж', 'Белая роза голландской селекции', 'шт', 120.00, 250.00, 10, 'Белый', 60),
(2, 'Тюльпан Монте Карло', 'Махровый желтый тюльпан', 'шт', 50.00, 100.00, 7, 'Желтый', 40),
(2, 'Тюльпан Апельдорн', 'Классический красный тюльпан', 'шт', 45.00, 90.00, 7, 'Красный', 45),
(3, 'Хризантема Сантини', 'Мелкоцветковая кустовая хризантема', 'шт', 70.00, 140.00, 14, 'Белый', 50),
(3, 'Хризантема одноголовая', 'Крупная хризантема для букетов', 'шт', 80.00, 160.00, 14, 'Желтый', 60),
(4, 'Гербера Джемсона', 'Крупная яркая гербера', 'шт', 65.00, 130.00, 12, 'Оранжевый', 55),
(4, 'Гербера мини', 'Мелкая гербера для композиций', 'шт', 55.00, 110.00, 12, 'Розовый', 40),
(5, 'Фаленопсис белый', 'Орхидея фаленопсис в горшке', 'шт', 500.00, 1200.00, 30, 'Белый', NULL),
(5, 'Дендробиум', 'Экзотическая орхидея дендробиум', 'шт', 450.00, 1000.00, 30, 'Фиолетовый', NULL);

-- 6. Партии поставок
INSERT INTO Batch (SupplierID, DeliveryDate, InvoiceNumber, Quantity, CostPrice) VALUES
(1, '2024-01-15', 'РОЗ-001/2024', 500, 75000.00),
(2, '2024-01-20', 'ТЮЛ-002/2024', 1000, 50000.00),
(3, '2024-01-25', 'ЭКВ-003/2024', 300, 45000.00),
(4, '2024-02-01', 'КЕН-004/2024', 400, 28000.00),
(5, '2024-02-05', 'ОРХ-005/2024', 50, 25000.00),
(6, '2024-02-10', 'РОС-006/2024', 600, 48000.00),
(7, '2024-02-15', 'ПИО-007/2024', 200, 16000.00),
(8, '2024-02-20', 'ЛИЛ-008/2024', 350, 24500.00),
(9, '2024-02-25', 'ГЕР-009/2024', 450, 29250.00),
(10, '2024-03-01', 'ЭКЗ-010/2024', 150, 22500.00);

-- 7. Заказы
INSERT INTO "Order" (ClientID, EmployeeID, ProductID, OrderDate, Status, OrderNumber, TotalAmount) VALUES
(1, 1, 1, '2024-01-20', 'Доставлен', 'ORD-001/2024', 1500.00),
(2, 3, 3, '2024-01-22', 'Выполнен', 'ORD-002/2024', 500.00),
(3, 1, 5, '2024-01-25', 'Доставлен', 'ORD-003/2024', 1120.00),
(4, 5, 2, '2024-01-28', 'В обработке', 'ORD-004/2024', 1250.00),
(5, 3, 7, '2024-02-01', 'Выполнен', 'ORD-005/2024', 780.00),
(6, 1, 4, '2024-02-05', 'Доставлен', 'ORD-006/2024', 720.00),
(7, 5, 6, '2024-02-10', 'В обработке', 'ORD-007/2024', 960.00),
(8, 3, 8, '2024-02-15', 'Выполнен', 'ORD-008/2024', 660.00),
(9, 1, 9, '2024-02-20', 'Доставлен', 'ORD-009/2024', 2400.00),
(10, 5, 10, '2024-02-25', 'В обработке', 'ORD-010/2024', 2000.00);

-- 8. Позиции заказов
INSERT INTO OrderPosition (OrderID, ProductID, Quantity, UnitPrice) VALUES
(1, 1, 5, 300.00),
(1, 2, 3, 250.00),
(2, 3, 5, 100.00),
(3, 5, 8, 140.00),
(4, 2, 5, 250.00),
(5, 7, 6, 130.00),
(6, 4, 8, 90.00),
(7, 6, 6, 160.00),
(8, 8, 6, 110.00),
(9, 9, 2, 1200.00);

-- 9. Складские позиции
INSERT INTO StockPosition (ProductID, BatchID, Quantity, ReceiptDate, StorageLocation, StorageTemperature, HumidityLevel) VALUES
(1, 1, 100, '2024-01-15', 'Холодильник А1', '+2°C', '85%'),
(2, 1, 80, '2024-01-15', 'Холодильник А2', '+2°C', '85%'),
(3, 2, 200, '2024-01-20', 'Холодильник Б1', '+4°C', '80%'),
(4, 2, 150, '2024-01-20', 'Холодильник Б2', '+4°C', '80%'),
(5, 4, 120, '2024-02-01', 'Холодильник В1', '+3°C', '75%'),
(6, 6, 100, '2024-02-10', 'Холодильник В2', '+3°C', '75%'),
(7, 9, 90, '2024-02-25', 'Холодильник Г1', '+5°C', '70%'),
(8, 9, 80, '2024-02-25', 'Холодильник Г2', '+5°C', '70%'),
(9, 5, 15, '2024-02-05', 'Теплица 1', '+18°C', '60%'),
(10, 10, 25, '2024-03-01', 'Теплица 2', '+20°C', '65%');

-- 10. Заполнение таблиц для обратной совместимости
INSERT INTO Inventory (ProductID, BatchID, Quantity, ReceiptDate, StorageLocation, StorageTemperature, HumidityLevel)
SELECT ProductID, BatchID, Quantity, ReceiptDate, StorageLocation, StorageTemperature, HumidityLevel FROM StockPosition;

INSERT INTO OrderItem (OrderID, ProductID, Quantity, UnitPrice)
SELECT OrderID, ProductID, Quantity, UnitPrice FROM OrderPosition;

-- ==========================================
-- Создание индексов для оптимизации
-- ==========================================

CREATE INDEX idx_product_category ON Product(CategoryID);
CREATE INDEX idx_batch_supplier ON Batch(SupplierID);
CREATE INDEX idx_order_client ON "Order"(ClientID);
CREATE INDEX idx_order_employee ON "Order"(EmployeeID);
CREATE INDEX idx_orderposition_order ON OrderPosition(OrderID);
CREATE INDEX idx_orderposition_product ON OrderPosition(ProductID);
CREATE INDEX idx_stockposition_product ON StockPosition(ProductID);
CREATE INDEX idx_stockposition_batch ON StockPosition(BatchID);

-- Индексы для таблиц обратной совместимости
CREATE INDEX idx_inventory_product ON Inventory(ProductID);
CREATE INDEX idx_inventory_batch ON Inventory(BatchID);
CREATE INDEX idx_orderitem_order ON OrderItem(OrderID);
CREATE INDEX idx_orderitem_product ON OrderItem(ProductID);

-- ==========================================
-- Анализ таблиц для оптимизации запросов
-- ==========================================
ANALYZE;

-- ==========================================
-- Завершение инициализации базы данных
-- ==========================================
DO $$
BEGIN
    RAISE NOTICE 'База данных ScladSimple успешно создана и заполнена';
    RAISE NOTICE 'Создано таблиц: 12 (включая таблицы обратной совместимости)';
    RAISE NOTICE 'Добавлено тестовых данных: Categories(10), Employees(10), Clients(10), Suppliers(10), Products(10), Batches(10), Orders(10), OrderPositions(10), StockPositions(10)';
END $$;
