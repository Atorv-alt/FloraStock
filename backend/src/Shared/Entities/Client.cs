using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace Shared.Entities
{
    public class Client
    {
        [JsonPropertyName("id")]
        public int ID { get; set; }
        
        // Поля для новой схемы
        [Required]
        [MaxLength(255)]
        [JsonPropertyName("fullName")]
        public string FullName { get; set; } = string.Empty;
        
        [MaxLength(20)]
        [JsonPropertyName("phoneNumber")]
        [RegularExpression(@"^\+7\d{10}$",
            ErrorMessage = "Телефон должен соответствовать формату +7XXXXXXXXXX")]
        public string? PhoneNumber { get; set; }
        
        [MaxLength(255)]
        [JsonPropertyName("email")]
        [EmailAddress(ErrorMessage = "Некорректный формат email-адреса")]
        public string? Email { get; set; }
        
        [JsonPropertyName("isActive")]
        public bool IsActive { get; set; } = true;
        
        // Поля для обратной совместимости
    }
}