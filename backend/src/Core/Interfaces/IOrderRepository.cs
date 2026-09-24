using Shared.Entities;
using Microsoft.EntityFrameworkCore.Storage;

namespace Core.Interfaces
{
    public interface IOrderRepository
    {
        Task<IEnumerable<Order>> GetAllAsync();
        Task<IEnumerable<Order>> GetByDateRangeAsync(DateTime startDate, DateTime endDate);
        Task<IEnumerable<Order>> GetByStatusAsync(string status);
        Task<IEnumerable<Order>> GetByClientAsync(int clientId);
        Task<IEnumerable<Order>> GetByEmployeeAsync(int employeeId);
        Task<Order?> GetByIdAsync(int id);
        Task<Order?> GetByOrderNumberAsync(string orderNumber);
        Task<Order> CreateAsync(Order order);
        Task<Order> UpdateAsync(Order order);
        Task<bool> DeleteAsync(int id);
        Task<bool> DeleteOrderWithItemsAsync(int orderId);
        Task<bool> ExistsAsync(int id);
        Task<bool> OrderNumberExistsAsync(string orderNumber, int? excludeId = null);
        Task<decimal> GetTotalRevenueAsync(DateTime? startDate = null, DateTime? endDate = null);
        Task<int> GetTotalOrdersAsync(DateTime? startDate = null, DateTime? endDate = null);
        
        // Order item management
        Task<IEnumerable<OrderItem>> GetOrderItemsAsync(int orderId);
        Task<OrderItem?> GetOrderItemAsync(int id);
        Task<OrderItem?> GetOrderItemAsync(int orderId, int productId);
        Task<OrderItem> CreateOrderItemAsync(OrderItem orderItem);
        Task<OrderItem> UpdateOrderItemAsync(OrderItem orderItem);
        Task<bool> DeleteOrderItemAsync(int id);
        
        // Transaction support
        Task<IDbContextTransaction> BeginTransactionAsync();
    }
}