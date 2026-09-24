using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.IdentityModel.Tokens;
using Core.Interfaces;
using Shared.Entities;

namespace Core.Services
{
    public class AuthService : IAuthService
    {
        private readonly IEmployeeRepository _employeeRepository;
        private readonly IConfiguration _configuration;
        private readonly ILogger<AuthService> _logger;

        public AuthService(
            IEmployeeRepository employeeRepository,
            IConfiguration configuration,
            ILogger<AuthService> logger)
        {
            _employeeRepository = employeeRepository;
            _configuration = configuration;
            _logger = logger;
        }

        public async Task<string?> AuthenticateAsync(string login, string password)
        {
            try
            {
                _logger.LogInformation("Попытка входа с логином: {Login}", login);
                
                var employee = await _employeeRepository.GetByLoginAsync(login);
                if (employee == null)
                {
                    _logger.LogWarning("Пользователь не найден с логином: {Login}", login);
                    return null;
                }

                // Сравнение хешей; пароли в лог не пишем
                if (employee.LoginPassword != PasswordHasher.Hash(password))
                {
                    _logger.LogWarning("Неверный пароль для логина: {Login}", login);
                    return null;
                }

                _logger.LogInformation("Аутентификация успешна для: {Login}", login);
                return await GenerateTokenAsync(employee);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при аутентификации пользователя: {Login}", login);
                return null;
            }
        }

        public async Task<Employee?> GetCurrentUserAsync(string token)
        {
            try
            {
                var tokenHandler = new JwtSecurityTokenHandler();
                var key = Encoding.UTF8.GetBytes(_configuration["Jwt:Key"]!);

                tokenHandler.ValidateToken(token, new TokenValidationParameters
                {
                    ValidateIssuerSigningKey = true,
                    IssuerSigningKey = new SymmetricSecurityKey(key),
                    ValidateIssuer = true,
                    ValidIssuer = _configuration["Jwt:Issuer"],
                    ValidateAudience = true,
                    ValidAudience = _configuration["Jwt:Audience"],
                    ValidateLifetime = true,
                    ClockSkew = TimeSpan.Zero
                }, out SecurityToken validatedToken);

                var jwtToken = (JwtSecurityToken)validatedToken;
                var userIdClaim = jwtToken.Claims.First(x => x.Type == "UserId").Value;
                
                if (int.TryParse(userIdClaim, out var userId))
                {
                    return await _employeeRepository.GetByIdAsync(userId);
                }

                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при валидации токена");
                return null;
            }
        }

        public async Task<bool> ValidateTokenAsync(string token)
        {
            var user = await GetCurrentUserAsync(token);
            return user != null;
        }

        public Task<string> GenerateTokenAsync(Employee employee)
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.UTF8.GetBytes(_configuration["Jwt:Key"]!);

            var claims = new List<Claim>
            {
                new Claim("UserId", employee.ID.ToString()),
                new Claim("FullName", employee.FullName),
                new Claim("AccessLevel", employee.AccessLevel ?? ""),
                new Claim("Position", employee.Position ?? ""),
                new Claim(JwtRegisteredClaimNames.Sub, employee.ID.ToString()),
                new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
                new Claim(JwtRegisteredClaimNames.Iat, DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString(), ClaimValueTypes.Integer64)
            };

            var tokenDescriptor = new SecurityTokenDescriptor
            {
                Subject = new ClaimsIdentity(claims),
                Expires = DateTime.UtcNow.AddDays(7),
                SigningCredentials = new SigningCredentials(new SymmetricSecurityKey(key), SecurityAlgorithms.HmacSha256Signature),
                Issuer = _configuration["Jwt:Issuer"],
                Audience = _configuration["Jwt:Audience"]
            };

            var token = tokenHandler.CreateToken(tokenDescriptor);
            return Task.FromResult(tokenHandler.WriteToken(token));
        }

        public async Task<bool> HasPermissionAsync(int employeeId, string permission)
        {
            try
            {
                var employee = await _employeeRepository.GetByIdAsync(employeeId);
                if (employee == null)
                    return false;

                // Простая проверка прав доступа
                return (employee.AccessLevel ?? "").ToLower() switch
                {
                    "admin" => true,
                    "manager" => permission != "system_admin",
                    "seller" => permission.Contains("read") || permission.Contains("order"),
                    "florist" => permission.Contains("product") || permission.Contains("inventory"),
                    "warehouse" => permission.Contains("inventory") || permission.Contains("batch"),
                    "courier" => permission.Contains("order") && permission.Contains("delivery"),
                    _ => false
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при проверке прав доступа");
                return false;
            }
        }

        public async Task<bool> ChangePasswordAsync(int employeeId, string currentPassword, string newPassword)
        {
            try
            {
                var employee = await _employeeRepository.GetByIdAsync(employeeId);
                if (employee == null)
                    return false;

                var currentPasswordHash = PasswordHasher.Hash(currentPassword);
                if (employee.LoginPassword != currentPasswordHash)
                    return false;

                employee.LoginPassword = PasswordHasher.Hash(newPassword);

                await _employeeRepository.UpdateAsync(employee);
                _logger.LogInformation("Пароль изменен для сотрудника: {EmployeeId}", employeeId);
                
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при изменении пароля для сотрудника: {EmployeeId}", employeeId);
                return false;
            }
        }

        public async Task<bool> ResetPasswordAsync(string email)
        {
            try
            {
                var employee = await _employeeRepository.GetByEmailAsync(email);
                if (employee == null)
                    return false;

                // Генерация временного пароля
                var tempPassword = GenerateTemporaryPassword();
                employee.LoginPassword = PasswordHasher.Hash(tempPassword);

                await _employeeRepository.UpdateAsync(employee);
                
                // Здесь должна быть отправка email с временным паролем
                _logger.LogInformation("Временный пароль сгенерирован для email: {Email}", email);
                
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при сбросе пароля для email: {Email}", email);
                return false;
            }
        }

        private string GenerateTemporaryPassword()
        {
            const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
            var random = new Random();
            return new string(Enumerable.Repeat(chars, 8)
                .Select(s => s[random.Next(s.Length)]).ToArray());
        }
    }
}