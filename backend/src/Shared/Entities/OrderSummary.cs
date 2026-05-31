using System.ComponentModel.DataAnnotations.Schema;

namespace Shared.Entities
{
    public class OrderSummary
    {
        public int Id { get; set; }
        
        public int OrderId { get; set; }
        
        public int TotalItems { get; set; } = 0;
        
        [Column(TypeName = "decimal(10,2)")]
        public decimal TotalAmount { get; set; } = 0.00m;
        
        [Column(TypeName = "decimal(10,2)")]
        public decimal AverageItemPrice { get; set; } = 0.00m;
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        // Навигационное свойство
        public virtual Order Order { get; set; } = null!;
    }
}