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
        public string? PhoneNumber { get; set; }
        
        [MaxLength(255)]
        public string? Email { get; set; }
        
        public string? Details { get; set; }
        
        public string? Address { get; set; }
        
        // Поля для обратной совместимости
    }
}