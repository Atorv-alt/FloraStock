using Shared.Entities;

namespace Core.Interfaces
{
    public interface IEmployeeRepository
    {
        Task<IEnumerable<Employee>> GetAllAsync();
        Task<IEnumerable<Employee>> GetActiveAsync();
        Task<Employee?> GetByIdAsync(int id);
        Task<Employee?> GetByLoginAsync(string login);
        Task<Employee?> GetByEmailAsync(string email);
        Task<Employee> CreateAsync(Employee employee);
        Task<Employee> UpdateAsync(Employee employee);
        Task<bool> DeleteAsync(int id);
        Task<bool> ExistsAsync(int id);
        Task<bool> LoginExistsAsync(string login, int? excludeId = null);
        Task<bool> EmailExistsAsync(string email, int? excludeId = null);
        Task<bool> ValidateCredentialsAsync(string login, string passwordHash);
    }
}