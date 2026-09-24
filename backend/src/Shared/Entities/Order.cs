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
        [RegularExpression("^(Новый|В обработке|Выполнен|Доставлен)$",
            ErrorMessage = "Статус должен быть: Новый, В обработке, Выполнен, Доставлен")]
        public string? Status { get; set; }
        
        [MaxLength(100)]
        [JsonPropertyName("orderNumber")]
        [RegularExpression(@"^ORD-\d{3,}/\d{4}$",
            ErrorMessage = "Номер заказа должен иметь формат ORD-XXX/ГГГГ")]
        public string? OrderNumber { get; set; }
        
        [JsonPropertyName("totalAmount")]
        [Range(0, 999999999.99, ErrorMessage = "Сумма заказа должна быть неотрицательной")]
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