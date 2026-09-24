using Shared.Entities;

namespace Core.Interfaces
{
    public interface IClientRepository
    {
        Task<IEnumerable<Client>> GetAllAsync();
        Task<IEnumerable<Client>> GetActiveAsync();
        Task<Client?> GetByIdAsync(int id);
        Task<Client?> GetByPhoneAsync(string phoneNumber);
        Task<Client?> GetByEmailAsync(string email);
        Task<Client> CreateAsync(Client client);
        Task<Client> UpdateAsync(Client client);
        Task<bool> DeleteAsync(int id);
        Task<bool> ExistsAsync(int id);
        Task<bool> PhoneExistsAsync(string phoneNumber, int? excludeId = null);
        Task<bool> EmailExistsAsync(string email, int? excludeId = null);
    }
}