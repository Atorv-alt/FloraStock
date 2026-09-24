using System.ComponentModel.DataAnnotations.Schema;

namespace Shared.Entities
{
    public class ProductCopy
    {
        public int Id { get; set; }
        
        public int ProductId { get; set; }
        
        public string? Name { get; set; }
        
        public string? Description { get; set; }
        
        [Column(TypeName = "decimal(10,2)")]
        public decimal? PurchasePrice { get; set; }
        
        [Column(TypeName = "decimal(10,2)")]
        public decimal? RetailPrice { get; set; }
        
        public DateTime CopyDate { get; set; } = DateTime.UtcNow;
        
        public string? OperationType { get; set; }
        
        // Навигационное свойство
        public virtual Product Product { get; set; } = null!;
    }
}