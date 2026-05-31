using System.ComponentModel.DataAnnotations;

namespace Shared.Entities
{
    public class OrderPosition
    {
        public int ID { get; set; }
        
        public int? OrderID { get; set; }
        
        public int? ProductID { get; set; }
        
        public int? Quantity { get; set; }
        
        public decimal? UnitPrice { get; set; }
    }
}
