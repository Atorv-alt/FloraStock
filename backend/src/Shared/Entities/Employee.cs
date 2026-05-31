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
        public string? PhoneNumber { get; set; }
        
        [MaxLength(255)]
        [JsonPropertyName("email")]
        public string? Email { get; set; }
        
        [MaxLength(255)]
        [JsonPropertyName("loginPassword")]
        public string? LoginPassword { get; set; }
        
        [MaxLength(50)]
        [JsonPropertyName("accessLevel")]
        public string? AccessLevel { get; set; }
        
        // Поля для обратной совместимости
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        public string? Login { get => LoginPassword; set => LoginPassword = value; }
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        public string? PasswordHash { get => LoginPassword; set => LoginPassword = value; }
    }
}