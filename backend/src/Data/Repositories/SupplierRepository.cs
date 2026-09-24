using Microsoft.EntityFrameworkCore;
using Core.Interfaces;
using Data;
using Shared.Entities;

namespace Data.Repositories
{
    public class SupplierRepository : ISupplierRepository
    {
        private readonly AppDbContext _context;

        public SupplierRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<Supplier>> GetAllAsync()
        {
            return await _context.Supplier
                .OrderBy(s => s.Name)
                .ToListAsync();
        }

        public async Task<IEnumerable<Supplier>> GetActiveAsync()
        {
            return await _context.Supplier
                .OrderBy(s => s.Name)
                .ToListAsync();
        }

        public async Task<Supplier?> GetByIdAsync(int id)
        {
            return await _context.Supplier
                .FirstOrDefaultAsync(s => s.ID == id);
        }

        public async Task<Supplier> CreateAsync(Supplier supplier)
        {
            _context.Supplier.Add(supplier);
            await _context.SaveChangesAsync();
            return supplier;
        }

        public async Task<Supplier> UpdateAsync(Supplier supplier)
        {
            _context.Supplier.Update(supplier);
            await _context.SaveChangesAsync();
            return supplier;
        }

        public async Task<bool> DeleteAsync(int id)
        {
            var supplier = await GetByIdAsync(id);
            if (supplier == null)
                return false;

            _context.Supplier.Remove(supplier);
            await _context.SaveChangesAsync();
            return true;
        }

        public async Task<bool> ExistsAsync(int id)
        {
            return await _context.Supplier.AnyAsync(s => s.ID == id);
        }

        public async Task<bool> NameExistsAsync(string name, int? excludeId = null)
        {
            var query = _context.Supplier.Where(s => s.Name.ToLower() == name.ToLower());
            
            if (excludeId.HasValue)
                query = query.Where(s => s.ID != excludeId.Value);

            return await query.AnyAsync();
        }
    }
}