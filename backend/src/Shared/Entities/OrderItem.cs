using System.ComponentModel.DataAnnotations;

namespace Shared.Entities
{
    public class OrderItem
    {
        public int ID { get; set; }
        
        // Поля для новой схемы
        public int? OrderID { get; set; }
        public int? ProductID { get; set; }
        [Range(0, int.MaxValue, ErrorMessage = "Количество в заказе должно быть неотрицательным целым числом")]
        public int? Quantity { get; set; }
        [Range(0.01, 999999999.99, ErrorMessage = "Цена должна быть положительным числом")]
        public decimal? UnitPrice { get; set; }
        
        // Поля для обратной совместимости
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        [System.Text.Json.Serialization.JsonIgnore]
        public int? OrderId { get => OrderID; set => OrderID = value; }
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        [System.Text.Json.Serialization.JsonIgnore]
        public int? ProductId { get => ProductID; set => ProductID = value; }
    }
}