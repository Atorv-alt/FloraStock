using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage;
using Core.Interfaces;
using Data;
using Shared.Entities;

namespace Data.Repositories
{
    public class InventoryRepository : IInventoryRepository
    {
        private readonly AppDbContext _context;

        public InventoryRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<Inventory>> GetAllAsync()
        {
            return await _context.Inventory
                .OrderBy(i => i.StorageLocation)
                .ToListAsync();
        }

        public async Task<IEnumerable<Inventory>> GetByProductAsync(int productId)
        {
            return await _context.Inventory
                .Where(i => i.ProductID == productId)
                .OrderByDescending(i => i.ReceiptDate)
                .ToListAsync();
        }

        public async Task<IEnumerable<Inventory>> GetByBatchAsync(int batchId)
        {
            return await _context.Inventory
                .Where(i => i.BatchID == batchId)
                .OrderBy(i => i.StorageLocation)
                .ToListAsync();
        }

        public async Task<IEnumerable<Inventory>> GetLowStockAsync(int threshold)
        {
            return await _context.Inventory
                .Where(i => i.Quantity <= threshold)
                .OrderBy(i => i.Quantity)
                .ThenBy(i => i.StorageLocation)
                .ToListAsync();
        }

        public async Task<IEnumerable<Inventory>> GetExpiringSoonAsync(int daysThreshold)
        {
            var expirationDate = DateTime.SpecifyKind(DateTime.Today.AddDays(daysThreshold), DateTimeKind.Utc);

            return await _context.Inventory
                .Where(i =>
                           i.ReceiptDate.HasValue &&
                           i.ReceiptDate.Value <= expirationDate)
                .OrderBy(i => i.ReceiptDate ?? new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc))
                .ThenBy(i => i.StorageLocation)
                .ToListAsync();
        }

        public async Task<Inventory?> GetByIdAsync(int id)
        {
            return await _context.Inventory
                .FirstOrDefaultAsync(i => i.ID == id);
        }

        public async Task<Inventory> CreateAsync(Inventory inventory)
        {
            _context.Inventory.Add(inventory);
            await _context.SaveChangesAsync();
            return inventory;
        }

        public async Task<Inventory> UpdateAsync(Inventory inventory)
        {
            _context.Inventory.Update(inventory);
            await _context.SaveChangesAsync();
            return inventory;
        }

        public async Task<bool> DeleteAsync(int id)
        {
            var inventory = await GetByIdAsync(id);
            if (inventory == null)
                return false;

            _context.Inventory.Remove(inventory);
            await _context.SaveChangesAsync();
            return true;
        }

        public async Task<bool> ExistsAsync(int id)
        {
            return await _context.Inventory.AnyAsync(i => i.ID == id);
        }

        public async Task<int> GetTotalQuantityAsync(int productId)
        {
            return await _context.Inventory
                .Where(i => i.ProductID == productId)
                .SumAsync(i => i.Quantity);
        }

        public async Task<decimal> GetTotalValueAsync()
        {
            return await _context.Inventory
                .Where(i => i.Quantity > 0)
                .Join(_context.Product,
                    inv => inv.ProductID,
                    prod => prod.ID,
                    (inv, prod) => new { inv.Quantity, prod.RetailPrice })
                .SumAsync(x => x.Quantity * (x.RetailPrice ?? 0m));
        }

        public async Task<bool> UpdateQuantityAsync(int id, int quantity)
        {
            var inventory = await _context.Inventory.FindAsync(id);
            if (inventory == null)
                return false;

            inventory.Quantity = quantity;
            
            await _context.SaveChangesAsync();
            return true;
        }

        public async Task<bool> TransferStockAsync(int fromId, int toId, int quantity)
        {
            using var transaction = await _context.Database.BeginTransactionAsync();
            
            try
            {
                var fromInventory = await _context.Inventory.FindAsync(fromId);
                var toInventory = await _context.Inventory.FindAsync(toId);

                if (fromInventory == null || toInventory == null || 
                    fromInventory.Quantity < quantity || quantity <= 0)
                {
                    await transaction.RollbackAsync();
                    return false;
                }

                fromInventory.Quantity -= quantity;

                toInventory.Quantity += quantity;

                await _context.SaveChangesAsync();
                await transaction.CommitAsync();
                return true;
            }
            catch
            {
                await transaction.RollbackAsync();
                return false;
            }
        }

        // Transaction support
        public async Task<IDbContextTransaction> BeginTransactionAsync()
        {
            return await _context.Database.BeginTransactionAsync();
        }


    }
}