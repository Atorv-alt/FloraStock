using System.ComponentModel.DataAnnotations;

namespace Shared.Entities
{
    public class OrderPosition
    {
        public int ID { get; set; }
        
        public int? OrderID { get; set; }
        
        public int? ProductID { get; set; }
        
        [Range(0, int.MaxValue, ErrorMessage = "Количество в заказе должно быть неотрицательным целым числом")]
        public int? Quantity { get; set; }
        
        [Range(0.01, 999999999.99, ErrorMessage = "Цена должна быть положительным числом")]
        public decimal? UnitPrice { get; set; }
    }
}
