using System.Text.Json.Serialization;
using Shared.Entities;

namespace API.DTOs
{
    public class OrderDto
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }
        
        [JsonPropertyName("clientId")]
        public int? ClientId { get; set; }
        
        [JsonPropertyName("employeeId")]
        public int? EmployeeId { get; set; }
        
        [JsonPropertyName("productId")]
        public int? ProductId { get; set; }
        
        [JsonPropertyName("orderDate")]
        public DateTime OrderDate { get; set; }
        
        [JsonPropertyName("status")]
        public string? Status { get; set; }
        
        [JsonPropertyName("orderNumber")]
        public string? OrderNumber { get; set; }
        
        [JsonPropertyName("totalAmount")]
        public decimal? TotalAmount { get; set; }
        
        // Данные клиента
        [JsonPropertyName("client")]
        public ClientDto? Client { get; set; }
        
        // Данные сотрудника
        [JsonPropertyName("employee")]
        public EmployeeDto? Employee { get; set; }
        
        public static OrderDto FromOrder(Order order, Client? client = null, Employee? employee = null)
        {
            return new OrderDto
            {
                Id = order.ID,
                ClientId = order.ClientID,
                EmployeeId = order.EmployeeID,
                ProductId = order.ProductID,
                OrderDate = order.OrderDate,
                Status = order.Status,
                OrderNumber = order.OrderNumber,
                TotalAmount = order.TotalAmount,
                Client = client != null ? ClientDto.FromClient(client) : null,
                Employee = employee != null ? EmployeeDto.FromEmployee(employee) : null
            };
        }
    }
    
    public class ClientDto
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }
        
        [JsonPropertyName("fullName")]
        public string? FullName { get; set; }
        
        [JsonPropertyName("phoneNumber")]
        public string? PhoneNumber { get; set; }
        
        [JsonPropertyName("email")]
        public string? Email { get; set; }
        
        [JsonPropertyName("isActive")]
        public bool IsActive { get; set; }
        
        public static ClientDto FromClient(Client client)
        {
            return new ClientDto
            {
                Id = client.ID,
                FullName = client.FullName,
                PhoneNumber = client.PhoneNumber,
                Email = client.Email,
                IsActive = true  // Default value since Client doesn't have IsActive
            };
        }
    }
    
    public class EmployeeDto
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }
        
        [JsonPropertyName("fullName")]
        public string? FullName { get; set; }
        
        [JsonPropertyName("position")]
        public string? Position { get; set; }
        
        [JsonPropertyName("phoneNumber")]
        public string? PhoneNumber { get; set; }
        
        [JsonPropertyName("email")]
        public string? Email { get; set; }
        
        [JsonPropertyName("accessLevel")]
        public string? AccessLevel { get; set; }
        
        public static EmployeeDto FromEmployee(Employee employee)
        {
            return new EmployeeDto
            {
                Id = employee.ID,
                FullName = employee.FullName,
                Position = employee.Position,
                PhoneNumber = employee.PhoneNumber,
                Email = employee.Email,
                AccessLevel = employee.AccessLevel
            };
        }
    }
}
