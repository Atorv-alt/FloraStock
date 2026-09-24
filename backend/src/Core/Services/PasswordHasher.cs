using System.Security.Cryptography;
using System.Text;

namespace Core.Services
{
    /// <summary>
    /// Единое место хеширования паролей.
    /// Схема: Base64(SHA256(password + "salt")).
    /// Используется AuthService, EmployeesController и стартовой нормализацией в Program.cs.
    /// </summary>
    public static class PasswordHasher
    {
        private const string Salt = "salt";

        public static string Hash(string password)
        {
            using var sha = SHA256.Create();
            var bytes = Encoding.UTF8.GetBytes(password + Salt);
            return Convert.ToBase64String(sha.ComputeHash(bytes));
        }

        /// <summary>
        /// Эвристика: значение уже является хешем (Base64, 44 символа, оканчивается на '=').
        /// Нужна для одноразовой миграции plaintext-паролей старых БД.
        /// </summary>
        public static bool LooksHashed(string? value)
        {
            if (string.IsNullOrEmpty(value) || value.Length != 44 || !value.EndsWith('='))
                return false;
            return value.All(c => char.IsLetterOrDigit(c) || c == '+' || c == '/' || c == '=');
        }
    }
}
