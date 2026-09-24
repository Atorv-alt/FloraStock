using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace Shared.Entities
{
    public class Employee
    {
        [JsonPropertyName("id")]
        public int ID { get; set; }
        
        // Поля для новой схемы
        [Required]
        [MaxLength(255)]
        [JsonPropertyName("fullName")]
        public string FullName { get; set; } = string.Empty;
        
        [MaxLength(100)]
        [JsonPropertyName("position")]
        public string? Position { get; set; }
        
        [MaxLength(20)]
        [JsonPropertyName("phoneNumber")]
        [RegularExpression(@"^\+7\d{10}$",
            ErrorMessage = "Телефон должен соответствовать формату +7XXXXXXXXXX")]
        public string? PhoneNumber { get; set; }
        
        [MaxLength(255)]
        [JsonPropertyName("email")]
        [EmailAddress(ErrorMessage = "Некорректный формат email-адреса")]
        public string? Email { get; set; }
        
        [MaxLength(100)]
        [JsonPropertyName("login")]
        public string? Login { get; set; }
        
        [MaxLength(255)]
        [JsonPropertyName("loginPassword")]
        [MinLength(1, ErrorMessage = "Пароль сотрудника не может быть пустым")]
        public string? LoginPassword { get; set; }
        
        [MaxLength(50)]
        [JsonPropertyName("accessLevel")]
        [RegularExpression("^(admin|florist|seller|purchasing|courier|warehouse)$",
            ErrorMessage = "Уровень доступа: admin, florist, seller, purchasing, courier, warehouse")]
        public string? AccessLevel { get; set; }
    }
}