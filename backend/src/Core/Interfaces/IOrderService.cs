using Shared.Entities;

namespace Core.Interfaces
{
    public interface IOrderService
    {
        Task<Order> CreateOrderAsync(Order order, List<OrderItem> orderItems);
        Task<Order> UpdateOrderAsync(Order order);
        Task<bool> CancelOrderAsync(int orderId);
        Task<bool> AddOrderItemAsync(int orderId, OrderItem orderItem);
        Task<bool> RemoveOrderItemAsync(int orderId, int productId);
        Task<bool> UpdateOrderItemAsync(int orderId, int productId, int quantity, decimal unitPrice);
        Task<bool> ProcessOrderAsync(int orderId);
        Task<bool> CompleteOrderAsync(int orderId);
        Task<decimal> CalculateOrderTotalAsync(int orderId);
        Task<bool> CheckInventoryAsync(List<OrderItem> orderItems);
        Task<bool> ReserveInventoryAsync(List<OrderItem> orderItems);
        Task<bool> ReleaseInventoryAsync(List<OrderItem> orderItems);
        Task<IEnumerable<Order>> GetOrdersByStatusAsync(string status);
        Task<IEnumerable<Order>> GetPendingOrdersAsync();
        Task<Order?> GetOrderWithItemsAsync(int orderId);
    }
}