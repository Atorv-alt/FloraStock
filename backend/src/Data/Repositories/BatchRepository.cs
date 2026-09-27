using Microsoft.EntityFrameworkCore;
using Core.Interfaces;
using Data;
using Shared.Entities;

namespace Data.Repositories
{
    public class BatchRepository : IBatchRepository
    {
        private readonly AppDbContext _context;

        public BatchRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<Batch>> GetAllAsync()
        {
            return await _context.Batch
                .OrderByDescending(b => b.DeliveryDate)
                .ToListAsync();
        }

        public async Task<IEnumerable<Batch>> GetBySupplierAsync(int supplierId)
        {
            return await _context.Batch
                .Where(b => b.SupplierID == supplierId)
                .OrderByDescending(b => b.DeliveryDate)
                .ToListAsync();
        }

        public async Task<IEnumerable<Batch>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
        {
            return await _context.Batch
                .Where(b => b.DeliveryDate >= startDate && b.DeliveryDate <= endDate)
                .OrderByDescending(b => b.DeliveryDate)
                .ToListAsync();
        }

        public async Task<Batch?> GetByIdAsync(int id)
        {
            return await _context.Batch
                .FirstOrDefaultAsync(b => b.ID == id);
        }

        public async Task<Batch?> GetByInvoiceNumberAsync(string invoiceNumber)
        {
            return await _context.Batch
                .FirstOrDefaultAsync(b => b.InvoiceNumber == invoiceNumber);
        }

        public async Task<Batch> CreateAsync(Batch batch)
        {
            _context.Batch.Add(batch);
            await _context.SaveChangesAsync();
            return batch;
        }

        public async Task<Batch> UpdateAsync(Batch batch)
        {
            _context.Batch.Update(batch);
            await _context.SaveChangesAsync();
            return batch;
        }

        public async Task<bool> DeleteAsync(int id)
        {
            var batch = await GetByIdAsync(id);
            if (batch == null)
                return false;

            _context.Batch.Remove(batch);
            await _context.SaveChangesAsync();
            return true;
        }

        public async Task<bool> ExistsAsync(int id)
        {
            return await _context.Batch.AnyAsync(b => b.ID == id);
        }

        public async Task<bool> InvoiceNumberExistsAsync(string invoiceNumber, int? excludeId = null)
        {
            var query = _context.Batch.Where(b => b.InvoiceNumber == invoiceNumber);
            
            if (excludeId.HasValue)
                query = query.Where(b => b.ID != excludeId.Value);

            return await query.AnyAsync();
        }

        public async Task<decimal> GetTotalCostAsync(DateTime? startDate = null, DateTime? endDate = null)
        {
            IQueryable<Batch> query = _context.Batch;

            if (startDate.HasValue)
                query = query.Where(b => b.DeliveryDate >= startDate.Value);

            if (endDate.HasValue)
                query = query.Where(b => b.DeliveryDate <= endDate.Value);

            return await query.SumAsync(b => b.CostPrice ?? 0m);
        }

        public async Task<int> GetTotalQuantityAsync(DateTime? startDate = null, DateTime? endDate = null)
        {
            IQueryable<Batch> query = _context.Batch;

            if (startDate.HasValue)
                query = query.Where(b => b.DeliveryDate >= startDate.Value);

            if (endDate.HasValue)
                query = query.Where(b => b.DeliveryDate <= endDate.Value);

            return await query.SumAsync(b => b.Quantity ?? 0);
        }
    }
}