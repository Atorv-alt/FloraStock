using Microsoft.EntityFrameworkCore;
using Core.Interfaces;
using Data;
using Shared.Entities;

namespace Data.Repositories
{
    public class EmployeeRepository : IEmployeeRepository
    {
        private readonly AppDbContext _context;

        public EmployeeRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<Employee>> GetAllAsync()
        {
            return await _context.Employee
                .OrderBy(e => e.FullName)
                .ToListAsync();
        }

        public async Task<IEnumerable<Employee>> GetActiveAsync()
        {
            return await _context.Employee
                .OrderBy(e => e.FullName)
                .ToListAsync();
        }

        public async Task<Employee?> GetByIdAsync(int id)
        {
            return await _context.Employee
                .FirstOrDefaultAsync(e => e.ID == id);
        }

        public async Task<Employee?> GetByLoginAsync(string login)
        {
            return await _context.Employee
                .FirstOrDefaultAsync(e => e.LoginPassword == login);
        }

        public async Task<Employee?> GetByEmailAsync(string email)
        {
            return await _context.Employee
                .FirstOrDefaultAsync(e => e.Email == email);
        }

        public async Task<Employee> CreateAsync(Employee employee)
        {
            _context.Employee.Add(employee);
            await _context.SaveChangesAsync();
            return employee;
        }

        public async Task<Employee> UpdateAsync(Employee employee)
        {
            _context.Employee.Update(employee);
            await _context.SaveChangesAsync();
            return employee;
        }

        public async Task<bool> DeleteAsync(int id)
        {
            var employee = await GetByIdAsync(id);
            if (employee == null)
                return false;

            _context.Employee.Remove(employee);
            await _context.SaveChangesAsync();
            return true;
        }

        public async Task<bool> ExistsAsync(int id)
        {
            return await _context.Employee.AnyAsync(e => e.ID == id);
        }

        public async Task<bool> LoginExistsAsync(string login, int? excludeId = null)
        {
            if (string.IsNullOrEmpty(login))
                return false;

            var query = _context.Employee.Where(e => e.FullName == login);
            
            if (excludeId.HasValue)
                query = query.Where(e => e.ID != excludeId.Value);

            return await query.AnyAsync();
        }

        public async Task<bool> EmailExistsAsync(string email, int? excludeId = null)
        {
            if (string.IsNullOrEmpty(email))
                return false;

            var query = _context.Employee.Where(e => e.Email == email);
            
            if (excludeId.HasValue)
                query = query.Where(e => e.ID != excludeId.Value);

            return await query.AnyAsync();
        }

        public async Task<bool> ValidateCredentialsAsync(string login, string passwordHash)
        {
            var employee = await GetByLoginAsync(login);
            if (employee == null || employee.LoginPassword != passwordHash)
                return false;
            
            return true;
        }
    }
}