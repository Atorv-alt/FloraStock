using Microsoft.EntityFrameworkCore;
using Core.Interfaces;
using Data;
using Shared.Entities;

namespace Data.Repositories
{
    public class ProductRepository : IProductRepository
    {
        private readonly AppDbContext _context;

        public ProductRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<Product>> GetAllAsync()
        {
            return await _context.Product
                .OrderBy(p => p.Name)
                .ToListAsync();
        }

        public async Task<IEnumerable<Product>> GetByCategoryAsync(int categoryId)
        {
            return await _context.Product
                .Where(p => p.CategoryId == categoryId)
                .OrderBy(p => p.Name)
                .ToListAsync();
        }

        public async Task<IEnumerable<Product>> GetActiveAsync()
        {
            return await _context.Product
                .OrderBy(p => p.Name)
                .ToListAsync();
        }

        public async Task<Product?> GetByIdAsync(int id)
        {
            return await _context.Product
                .FirstOrDefaultAsync(p => p.ID == id);
        }

        public async Task<Product> CreateAsync(Product product)
        {
            _context.Product.Add(product);
            await _context.SaveChangesAsync();
            return product;
        }

        public async Task<Product> UpdateAsync(Product product)
        {
            _context.Product.Update(product);
            await _context.SaveChangesAsync();
            return product;
        }

        public async Task<bool> DeleteAsync(int id)
        {
            var product = await GetByIdAsync(id);
            if (product == null)
                return false;

            _context.Product.Remove(product);
            await _context.SaveChangesAsync();
            return true;
        }

        public async Task<bool> ExistsAsync(int id)
        {
            return await _context.Product.AnyAsync(p => p.ID == id);
        }

        public async Task<bool> NameExistsAsync(string name, int? excludeId = null)
        {
            var query = _context.Product.Where(p => p.Name.ToLower() == name.ToLower());
            
            if (excludeId.HasValue)
                query = query.Where(p => p.ID != excludeId.Value);

            return await query.AnyAsync();
        }

        public async Task<decimal> GetTotalInventoryValueAsync()
        {
            try
            {
                var inventory = await _context.Inventory
                    .Where(i => i.Quantity > 0)
                    .ToListAsync();

                decimal totalValue = 0;
                foreach (var item in inventory)
                {
                    var product = await _context.Product
                        .FirstOrDefaultAsync(p => p.ID == item.ProductId);
                    if (product != null)
                    {
                        totalValue += item.Quantity * (product.RetailPrice ?? 0m);
                    }
                }
                return totalValue;
            }
            catch (Exception ex)
            {
                throw new Exception("Ошибка при расчете стоимости склада", ex);
            }
        }

        public async Task<IEnumerable<Product>> GetLowStockAsync(int threshold)
        {
            var lowStockProductIds = await _context.Inventory
                .Where(i => i.Quantity <= threshold)
                .Select(i => i.ProductId)
                .Distinct()
                .ToListAsync();

            return await _context.Product
                .Where(p => lowStockProductIds.Contains(p.ID))
                .ToListAsync();
        }
    }
}