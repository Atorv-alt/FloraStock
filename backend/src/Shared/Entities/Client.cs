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
        public string? PhoneNumber { get; set; }
        
        [MaxLength(255)]
        [JsonPropertyName("email")]
        public string? Email { get; set; }
        
        // Поля для обратной совместимости
    }
}