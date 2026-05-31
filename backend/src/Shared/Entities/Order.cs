using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace Shared.Entities
{
    public class Order
    {
        [JsonPropertyName("id")]
        public int ID { get; set; }
        
        // Поля для новой схемы
        [JsonPropertyName("clientId")]
        public int? ClientID { get; set; }
        
        [JsonPropertyName("employeeId")]
        public int? EmployeeID { get; set; }
        
        [JsonPropertyName("productId")]
        public int? ProductID { get; set; }
        
        [JsonPropertyName("orderDate")]
        public DateTime OrderDate { get; set; }
        
        [MaxLength(50)]
        [JsonPropertyName("status")]
        public string? Status { get; set; }
        
        [MaxLength(100)]
        [JsonPropertyName("orderNumber")]
        public string? OrderNumber { get; set; }
        
        [JsonPropertyName("totalAmount")]
        public decimal? TotalAmount { get; set; }
        
        // Поля для обратной совместимости
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        [System.Text.Json.Serialization.JsonIgnore]
        public int? ClientId { get => ClientID; set => ClientID = value; }
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        [System.Text.Json.Serialization.JsonIgnore]
        public int? EmployeeId { get => EmployeeID; set => EmployeeID = value; }
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        [System.Text.Json.Serialization.JsonIgnore]
        public int? ProductId { get => ProductID; set => ProductID = value; }
    }
}