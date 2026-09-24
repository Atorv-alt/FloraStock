using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace Shared.Entities
{
    public class Batch
    {
        [JsonPropertyName("id")]
        public int ID { get; set; }
        
        // Поля для новой схемы
        [JsonPropertyName("supplierId")]
        public int? SupplierID { get; set; }
        
        [JsonPropertyName("deliveryDate")]
        public DateTime? DeliveryDate { get; set; }
        
        [MaxLength(100)]
        [JsonPropertyName("invoiceNumber")]
        [RegularExpression(@"^[А-ЯЁA-Z]{2,5}-\d{3,}/\d{4}$",
            ErrorMessage = "Номер накладной должен иметь формат ХХХ-YYY/ГГГГ")]
        public string? InvoiceNumber { get; set; }
        
        [JsonPropertyName("quantity")]
        [Range(0, int.MaxValue, ErrorMessage = "Количество в партии должно быть неотрицательным целым числом")]
        public int? Quantity { get; set; }
        
        [JsonPropertyName("costPrice")]
        [Range(0.01, 999999999.99, ErrorMessage = "Стоимость партии должна быть положительным числом")]
        public decimal? CostPrice { get; set; }
        
        // Поля для обратной совместимости
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        [System.Text.Json.Serialization.JsonIgnore]
        public int? SupplierId { get => SupplierID; set => SupplierID = value; }
    }
}