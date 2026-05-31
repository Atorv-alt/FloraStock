using Microsoft.EntityFrameworkCore;
using Shared.Entities;

namespace Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
        {
        }

        // DbSets для репозиториев (в единственном числе для соответствия базе данных)
        public DbSet<Category> Category { get; set; }
        public DbSet<Product> Product { get; set; }
        public DbSet<Client> Client { get; set; }
        public DbSet<Employee> Employee { get; set; }
        public DbSet<Supplier> Supplier { get; set; }
        public DbSet<Order> Order { get; set; }
        public DbSet<OrderPosition> OrderPosition { get; set; }
        public DbSet<Batch> Batch { get; set; }
        public DbSet<Inventory> Inventory { get; set; }
        public DbSet<OrderItem> OrderItem { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            
            // Настройка имен таблиц для соответствия базе данных (в нижнем регистре)
            modelBuilder.Entity<Category>().ToTable("Category");
            modelBuilder.Entity<Product>().ToTable("Product");
            modelBuilder.Entity<Client>().ToTable("Client");
            modelBuilder.Entity<Employee>().ToTable("Employee");
            modelBuilder.Entity<Supplier>().ToTable("Supplier");
            modelBuilder.Entity<Order>().ToTable("\"Order\"");
            modelBuilder.Entity<OrderPosition>().ToTable("OrderPosition");
            modelBuilder.Entity<Batch>().ToTable("Batch");
            modelBuilder.Entity<Inventory>().ToTable("StockPosition");
            modelBuilder.Entity<OrderItem>().ToTable("OrderItem");
            
            // Используем простые конфигурации только для ключей и имен столбцов
            modelBuilder.Entity<Category>().HasKey(e => e.ID);
            modelBuilder.Entity<Product>().HasKey(e => e.ID);
            modelBuilder.Entity<Client>().HasKey(e => e.ID);
            modelBuilder.Entity<Employee>().HasKey(e => e.ID);
            modelBuilder.Entity<Supplier>().HasKey(e => e.ID);
            modelBuilder.Entity<Order>().HasKey(e => e.ID);
            modelBuilder.Entity<OrderPosition>().HasKey(e => e.ID);
            modelBuilder.Entity<Batch>().HasKey(e => e.ID);
            modelBuilder.Entity<Inventory>().HasKey(e => e.ID);
            modelBuilder.Entity<OrderItem>().HasKey(e => e.ID);
            
            // Конфигурация имен столбцов для соответствия базе данных
            modelBuilder.Entity<Employee>().Property(e => e.ID).HasColumnName("id");
            modelBuilder.Entity<Employee>().Property(e => e.FullName).HasColumnName("fullname");
            modelBuilder.Entity<Employee>().Property(e => e.Position).HasColumnName("position");
            modelBuilder.Entity<Employee>().Property(e => e.PhoneNumber).HasColumnName("phonenumber");
            modelBuilder.Entity<Employee>().Property(e => e.Email).HasColumnName("email");
            modelBuilder.Entity<Employee>().Property(e => e.LoginPassword).HasColumnName("loginpassword");
            modelBuilder.Entity<Employee>().Property(e => e.AccessLevel).HasColumnName("accesslevel");
            
            // Product table column mappings
            modelBuilder.Entity<Product>().Property(e => e.ID).HasColumnName("id");
            modelBuilder.Entity<Product>().Property(e => e.CategoryID).HasColumnName("categoryid");
            modelBuilder.Entity<Product>().Property(e => e.Name).HasColumnName("name");
            modelBuilder.Entity<Product>().Property(e => e.Description).HasColumnName("description");
            modelBuilder.Entity<Product>().Property(e => e.Unit).HasColumnName("unit");
            modelBuilder.Entity<Product>().Property(e => e.PurchasePrice).HasColumnName("purchaseprice");
            modelBuilder.Entity<Product>().Property(e => e.RetailPrice).HasColumnName("retailprice");
            modelBuilder.Entity<Product>().Property(e => e.ShelfLifeDays).HasColumnName("shelflifedays");
            modelBuilder.Entity<Product>().Property(e => e.Color).HasColumnName("color");
            modelBuilder.Entity<Product>().Property(e => e.StemLengthCm).HasColumnName("stemlengthcm");
            
            // Category table column mappings
            modelBuilder.Entity<Category>().Property(e => e.ID).HasColumnName("id");
            modelBuilder.Entity<Category>().Property(e => e.Name).HasColumnName("name");
            modelBuilder.Entity<Category>().Property(e => e.Description).HasColumnName("description");
            
            // Client table column mappings
            modelBuilder.Entity<Client>().Property(e => e.ID).HasColumnName("id");
            modelBuilder.Entity<Client>().Property(e => e.FullName).HasColumnName("fullname");
            modelBuilder.Entity<Client>().Property(e => e.PhoneNumber).HasColumnName("phonenumber");
            modelBuilder.Entity<Client>().Property(e => e.Email).HasColumnName("email");
            
            // Order table column mappings
            modelBuilder.Entity<Order>().Property(e => e.ID).HasColumnName("id");
            modelBuilder.Entity<Order>().Property(e => e.ClientID).HasColumnName("clientid");
            modelBuilder.Entity<Order>().Property(e => e.EmployeeID).HasColumnName("employeeid");
            modelBuilder.Entity<Order>().Property(e => e.ProductID).HasColumnName("productid");
            modelBuilder.Entity<Order>().Property(e => e.OrderDate).HasColumnName("orderdate");
            modelBuilder.Entity<Order>().Property(e => e.OrderNumber).HasColumnName("ordernumber");
            modelBuilder.Entity<Order>().Property(e => e.Status).HasColumnName("status");
            modelBuilder.Entity<Order>().Property(e => e.TotalAmount).HasColumnName("totalamount");
            
            // Supplier table column mappings
            modelBuilder.Entity<Supplier>().Property(e => e.ID).HasColumnName("id");
            modelBuilder.Entity<Supplier>().Property(e => e.Name).HasColumnName("name");
            modelBuilder.Entity<Supplier>().Property(e => e.PhoneNumber).HasColumnName("phonenumber");
            modelBuilder.Entity<Supplier>().Property(e => e.Email).HasColumnName("email");
            modelBuilder.Entity<Supplier>().Property(e => e.Details).HasColumnName("details");
            modelBuilder.Entity<Supplier>().Property(e => e.Address).HasColumnName("address");
            
            // Batch table column mappings
            modelBuilder.Entity<Batch>().Property(e => e.ID).HasColumnName("id");
            modelBuilder.Entity<Batch>().Property(e => e.SupplierID).HasColumnName("supplierid");
            modelBuilder.Entity<Batch>().Property(e => e.DeliveryDate).HasColumnName("deliverydate");
            modelBuilder.Entity<Batch>().Property(e => e.InvoiceNumber).HasColumnName("invoicenumber");
            modelBuilder.Entity<Batch>().Property(e => e.Quantity).HasColumnName("quantity");
            modelBuilder.Entity<Batch>().Property(e => e.CostPrice).HasColumnName("costprice");
            
            // OrderItem table column mappings
            modelBuilder.Entity<OrderItem>().Property(e => e.ID).HasColumnName("id");
            modelBuilder.Entity<OrderItem>().Property(e => e.OrderID).HasColumnName("orderid");
            modelBuilder.Entity<OrderItem>().Property(e => e.ProductID).HasColumnName("productid");
            modelBuilder.Entity<OrderItem>().Property(e => e.Quantity).HasColumnName("quantity");
            modelBuilder.Entity<OrderItem>().Property(e => e.UnitPrice).HasColumnName("unitprice");
            
            // Inventory table column mappings
            modelBuilder.Entity<Inventory>().Property(e => e.ID).HasColumnName("id");
            modelBuilder.Entity<Inventory>().Property(e => e.ProductID).HasColumnName("productid");
            modelBuilder.Entity<Inventory>().Property(e => e.BatchID).HasColumnName("batchid");
            modelBuilder.Entity<Inventory>().Property(e => e.Quantity).HasColumnName("quantity");
            modelBuilder.Entity<Inventory>().Property(e => e.ReceiptDate).HasColumnName("receiptdate");
            modelBuilder.Entity<Inventory>().Property(e => e.StorageLocation).HasColumnName("storagelocation");
            modelBuilder.Entity<Inventory>().Property(e => e.StorageTemperature).HasColumnName("storagetemperature");
            modelBuilder.Entity<Inventory>().Property(e => e.HumidityLevel).HasColumnName("humiditylevel");
            
            // OrderPosition table column mappings
            modelBuilder.Entity<OrderPosition>().Property(e => e.ID).HasColumnName("id");
            modelBuilder.Entity<OrderPosition>().Property(e => e.OrderID).HasColumnName("orderid");
            modelBuilder.Entity<OrderPosition>().Property(e => e.ProductID).HasColumnName("productid");
            modelBuilder.Entity<OrderPosition>().Property(e => e.Quantity).HasColumnName("quantity");
            modelBuilder.Entity<OrderPosition>().Property(e => e.UnitPrice).HasColumnName("unitprice");
        }
    }
}
