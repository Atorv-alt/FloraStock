using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace Shared.Entities
{
    public class Inventory
    {
        [JsonPropertyName("id")]
        public int ID { get; set; }
        
        // Поля для новой схемы
        [JsonPropertyName("productId")]
        public int? ProductID { get; set; }
        [JsonPropertyName("batchId")]
        public int? BatchID { get; set; }
        [JsonPropertyName("quantity")]
        [Range(0, int.MaxValue, ErrorMessage = "Количество на складе должно быть неотрицательным целым числом")]
        public int Quantity { get; set; } = 0;
        [JsonPropertyName("receiptDate")]
        public DateTime? ReceiptDate { get; set; }
        [MaxLength(255)]
        [JsonPropertyName("storageLocation")]
        public string? StorageLocation { get; set; }
        [MaxLength(50)]
        [JsonPropertyName("storageTemperature")]
        public string? StorageTemperature { get; set; }
        [MaxLength(50)]
        [JsonPropertyName("humidityLevel")]
        public string? HumidityLevel { get; set; }
        
        // Поля для обратной совместимости
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        [System.Text.Json.Serialization.JsonIgnore]
        public int? ProductId { get => ProductID; set => ProductID = value; }
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        [System.Text.Json.Serialization.JsonIgnore]
        public int? BatchId { get => BatchID; set => BatchID = value; }
    }
}