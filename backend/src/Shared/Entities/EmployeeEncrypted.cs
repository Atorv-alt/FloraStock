namespace Shared.Entities
{
    public class EmployeeEncrypted
    {
        public int Id { get; set; }
        
        public int EmployeeId { get; set; }
        
        public string? PassportData { get; set; }
        
        public string? BankDetails { get; set; }
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
        
        // Навигационное свойство
        public virtual Employee Employee { get; set; } = null!;
    }
}