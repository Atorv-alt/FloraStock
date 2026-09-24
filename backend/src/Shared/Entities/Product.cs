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
        [RegularExpression(@"^[А-ЯЁA-Za-zа-яё\s\-]+$",
            ErrorMessage = "Единица измерения должна содержать только буквы (например: шт, кг, букет)")]
        public string? Unit { get; set; }
        
        [JsonPropertyName("purchasePrice")]
        [Range(0.01, 999999999.99, ErrorMessage = "Закупочная цена должна быть положительным числом")]
        public decimal? PurchasePrice { get; set; }
        
        [JsonPropertyName("retailPrice")]
        [Range(0.01, 999999999.99, ErrorMessage = "Розничная цена должна быть положительным числом")]
        public decimal? RetailPrice { get; set; }
        
        [JsonPropertyName("shelfLifeDays")]
        [Range(1, 36500, ErrorMessage = "Срок хранения должен быть положительным целым числом")]
        public int? ShelfLifeDays { get; set; }
        
        [MaxLength(50)]
        [JsonPropertyName("color")]
        [RegularExpression(@"^[А-ЯЁA-Za-zа-яё\s\-]+$",
            ErrorMessage = "Цвет должен содержать только буквы (например: красный, белый)")]
        public string? Color { get; set; }
        
        [JsonPropertyName("stemLengthCm")]
        public int? StemLengthCm { get; set; }
        
        // Поля для обратной совместимости
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        [System.Text.Json.Serialization.JsonIgnore]
        public int? CategoryId { get => CategoryID; set => CategoryID = value; }
    }
}