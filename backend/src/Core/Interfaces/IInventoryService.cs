using Shared.Entities;

namespace Core.Interfaces
{
    public interface IInventoryService
    {
        Task<Inventory> AddInventoryAsync(Inventory inventory);
        Task<bool> UpdateInventoryAsync(int id, int quantity);
        Task<bool> RemoveInventoryAsync(int id, int quantity);
        Task<bool> TransferInventoryAsync(int fromId, int toId, int quantity);
        Task<IEnumerable<Inventory>> GetLowStockItemsAsync(int threshold);
        Task<IEnumerable<Inventory>> GetExpiringItemsAsync(int daysThreshold);
        Task<bool> ProcessBatchReceiptAsync(Batch batch, List<Inventory> inventoryItems);
        Task<decimal> GetInventoryValueAsync();
        Task<int> GetTotalStockAsync();
        Task<Dictionary<string, int>> GetStockByCategoryAsync();
        Task<bool> ValidateInventoryAvailabilityAsync(List<OrderItem> orderItems);
        Task<bool> ReserveStockAsync(List<OrderItem> orderItems);
        Task<bool> ReleaseStockAsync(List<OrderItem> orderItems);
        Task<bool> ConsumeStockAsync(List<OrderItem> orderItems);
        Task<Inventory?> GetProductInventoryAsync(int productId);
    }
}