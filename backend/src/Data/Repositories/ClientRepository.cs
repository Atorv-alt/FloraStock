using Microsoft.EntityFrameworkCore;
using Core.Interfaces;
using Data;
using Shared.Entities;

namespace Data.Repositories
{
    public class ClientRepository : IClientRepository
    {
        private readonly AppDbContext _context;

        public ClientRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<Client>> GetAllAsync()
        {
            return await _context.Client
                .OrderBy(c => c.FullName)
                .ToListAsync();
        }

        public async Task<IEnumerable<Client>> GetActiveAsync()
        {
            return await _context.Client
                .OrderBy(c => c.FullName)
                .ToListAsync();
        }

        public async Task<Client?> GetByIdAsync(int id)
        {
            return await _context.Client
                .FirstOrDefaultAsync(c => c.ID == id);
        }

        public async Task<Client?> GetByPhoneAsync(string phoneNumber)
        {
            return await _context.Client
                .FirstOrDefaultAsync(c => c.PhoneNumber == phoneNumber);
        }

        public async Task<Client?> GetByEmailAsync(string email)
        {
            return await _context.Client
                .FirstOrDefaultAsync(c => c.Email == email);
        }

        public async Task<Client> CreateAsync(Client client)
        {
            _context.Client.Add(client);
            await _context.SaveChangesAsync();
            return client;
        }

        public async Task<Client> UpdateAsync(Client client)
        {
            _context.Client.Update(client);
            await _context.SaveChangesAsync();
            return client;
        }

        public async Task<bool> DeleteAsync(int id)
        {
            var client = await GetByIdAsync(id);
            if (client == null)
                return false;

            _context.Client.Remove(client);
            await _context.SaveChangesAsync();
            return true;
        }

        public async Task<bool> ExistsAsync(int id)
        {
            return await _context.Client.AnyAsync(c => c.ID == id);
        }

        public async Task<bool> PhoneExistsAsync(string phoneNumber, int? excludeId = null)
        {
            if (string.IsNullOrEmpty(phoneNumber))
                return false;

            var query = _context.Client.Where(c => c.PhoneNumber == phoneNumber);
            
            if (excludeId.HasValue)
                query = query.Where(c => c.ID != excludeId.Value);

            return await query.AnyAsync();
        }

        public async Task<bool> EmailExistsAsync(string email, int? excludeId = null)
        {
            if (string.IsNullOrEmpty(email))
                return false;

            var query = _context.Client.Where(c => c.Email == email);
            
            if (excludeId.HasValue)
                query = query.Where(c => c.ID != excludeId.Value);

            return await query.AnyAsync();
        }
    }
}