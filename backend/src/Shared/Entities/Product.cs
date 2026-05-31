using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace Shared.Entities
{
    public class Product
    {
        [JsonPropertyName("id")]
        public int ID { get; set; }
        
        // Поля для новой схемы
        [JsonPropertyName("categoryId")]
        public int? CategoryID { get; set; }
        
        [Required]
        [MaxLength(255)]
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;
        
        [JsonPropertyName("description")]
        public string? Description { get; set; }
        
        [MaxLength(50)]
        [JsonPropertyName("unit")]
        public string? Unit { get; set; }
        
        [JsonPropertyName("purchasePrice")]
        public decimal? PurchasePrice { get; set; }
        
        [JsonPropertyName("retailPrice")]
        public decimal? RetailPrice { get; set; }
        
        [JsonPropertyName("shelfLifeDays")]
        public int? ShelfLifeDays { get; set; }
        
        [MaxLength(50)]
        [JsonPropertyName("color")]
        public string? Color { get; set; }
        
        [JsonPropertyName("stemLengthCm")]
        public int? StemLengthCm { get; set; }
        
        // Поля для обратной совместимости
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        [System.Text.Json.Serialization.JsonIgnore]
        public int? CategoryId { get => CategoryID; set => CategoryID = value; }
    }
}