using System.ComponentModel.DataAnnotations.Schema;

namespace Shared.Entities
{
    public class DeletedProduct
    {
        public int Id { get; set; }
        
        public int ProductId { get; set; }
        
        public int? CategoryId { get; set; }
        
        public string? Name { get; set; }
        
        public string? Description { get; set; }
        
        public string? Unit { get; set; }
        
        [Column(TypeName = "decimal(10,2)")]
        public decimal? PurchasePrice { get; set; }
        
        [Column(TypeName = "decimal(10,2)")]
        public decimal? RetailPrice { get; set; }
        
        public int? ShelfLifeDays { get; set; }
        
        public string? Color { get; set; }
        
        public int? StemLengthCm { get; set; }
        
        public DateTime DeletedAt { get; set; } = DateTime.UtcNow;
        
        public int? DeletedBy { get; set; }
        
        // Навигационное свойство
        public virtual Employee? DeletedByEmployee { get; set; }
    }
}