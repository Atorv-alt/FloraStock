using System.ComponentModel.DataAnnotations;

namespace Shared.Entities
{
    public class StockPosition
    {
        public int ID { get; set; }
        
        public int? ProductID { get; set; }
        
        public int? BatchID { get; set; }
        
        [Range(0, int.MaxValue, ErrorMessage = "Количество на складе должно быть неотрицательным целым числом")]
        public int? Quantity { get; set; }
        
        public DateTime? ReceiptDate { get; set; }
        
        [MaxLength(255)]
        public string? StorageLocation { get; set; }
        
        [MaxLength(50)]
        public string? StorageTemperature { get; set; }
        
        [MaxLength(50)]
        public string? HumidityLevel { get; set; }
    }
}
