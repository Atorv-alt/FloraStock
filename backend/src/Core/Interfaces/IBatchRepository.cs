using Shared.Entities;

namespace Core.Interfaces
{
    public interface IBatchRepository
    {
        Task<IEnumerable<Batch>> GetAllAsync();
        Task<IEnumerable<Batch>> GetBySupplierAsync(int supplierId);
        Task<IEnumerable<Batch>> GetByDateRangeAsync(DateTime startDate, DateTime endDate);
        Task<Batch?> GetByIdAsync(int id);
        Task<Batch?> GetByInvoiceNumberAsync(string invoiceNumber);
        Task<Batch> CreateAsync(Batch batch);
        Task<Batch> UpdateAsync(Batch batch);
        Task<bool> DeleteAsync(int id);
        Task<bool> ExistsAsync(int id);
        Task<bool> InvoiceNumberExistsAsync(string invoiceNumber, int? excludeId = null);
        Task<decimal> GetTotalCostAsync(DateTime? startDate = null, DateTime? endDate = null);
        Task<int> GetTotalQuantityAsync(DateTime? startDate = null, DateTime? endDate = null);
    }
}