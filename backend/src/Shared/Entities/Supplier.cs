using System.ComponentModel.DataAnnotations;

namespace Shared.Entities
{
    public class Supplier
    {
        public int ID { get; set; }
        
        // Поля для новой схемы
        [Required]
        [MaxLength(255)]
        public string Name { get; set; } = string.Empty;
        
        [MaxLength(20)]
        [RegularExpression(@"^\+7\d{10}$",
            ErrorMessage = "Телефон должен соответствовать формату +7XXXXXXXXXX")]
        public string? PhoneNumber { get; set; }
        
        [MaxLength(255)]
        [EmailAddress(ErrorMessage = "Некорректный формат email-адреса")]
        public string? Email { get; set; }
        
        public string? Details { get; set; }
        
        public string? Address { get; set; }
        
        // Поля для обратной совместимости
    }
}