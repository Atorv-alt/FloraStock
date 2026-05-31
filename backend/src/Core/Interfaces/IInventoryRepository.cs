using Shared.Entities;
using Microsoft.EntityFrameworkCore.Storage;

namespace Core.Interfaces
{
    public interface IInventoryRepository
    {
        Task<IEnumerable<Inventory>> GetAllAsync();
        Task<IEnumerable<Inventory>> GetByProductAsync(int productId);
        Task<IEnumerable<Inventory>> GetByBatchAsync(int batchId);
        Task<IEnumerable<Inventory>> GetLowStockAsync(int threshold);
        Task<IEnumerable<Inventory>> GetExpiringSoonAsync(int daysThreshold);
        Task<Inventory?> GetByIdAsync(int id);
        Task<Inventory> CreateAsync(Inventory inventory);
        Task<Inventory> UpdateAsync(Inventory inventory);
        Task<bool> DeleteAsync(int id);
        Task<bool> ExistsAsync(int id);
        Task<int> GetTotalQuantityAsync(int productId);
        Task<decimal> GetTotalValueAsync();
        Task<bool> UpdateQuantityAsync(int id, int quantity);
        Task<bool> TransferStockAsync(int fromId, int toId, int quantity);
        
        // Transaction support
        Task<IDbContextTransaction> BeginTransactionAsync();
    }
}