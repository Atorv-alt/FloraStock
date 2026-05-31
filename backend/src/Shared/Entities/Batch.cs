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
        public string? InvoiceNumber { get; set; }
        
        [JsonPropertyName("quantity")]
        public int? Quantity { get; set; }
        
        [JsonPropertyName("costPrice")]
        public decimal? CostPrice { get; set; }
        
        // Поля для обратной совместимости
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        [System.Text.Json.Serialization.JsonIgnore]
        public int? SupplierId { get => SupplierID; set => SupplierID = value; }
    }
}