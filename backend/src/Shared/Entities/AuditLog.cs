namespace Shared.Entities
{
    public class AuditLog
    {
        public int Id { get; set; }
        
        public string? TableName { get; set; }
        
        public int? RecordId { get; set; }
        
        public string? Operation { get; set; }
        
        public string? OldValues { get; set; }
        
        public string? NewValues { get; set; }
        
        public int? UserId { get; set; }
        
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        
        // Навигационное свойство
        public virtual Employee? User { get; set; }
    }
}