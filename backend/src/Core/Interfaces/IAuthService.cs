using Shared.Entities;

namespace Core.Interfaces
{
    public interface IAuthService
    {
        Task<string?> AuthenticateAsync(string login, string password);
        Task<Employee?> GetCurrentUserAsync(string token);
        Task<bool> ValidateTokenAsync(string token);
        Task<string> GenerateTokenAsync(Employee employee);
        Task<bool> HasPermissionAsync(int employeeId, string permission);
        Task<bool> ChangePasswordAsync(int employeeId, string currentPassword, string newPassword);
        Task<bool> ResetPasswordAsync(string email);
    }
}