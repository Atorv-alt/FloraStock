using Core.Interfaces;
using Shared.Entities;
using Microsoft.Extensions.Logging;

namespace Core.Services
{
    public class InventoryService : IInventoryService
    {
        private readonly IInventoryRepository _inventoryRepository;
        private readonly IProductRepository _productRepository;
        private readonly IBatchRepository _batchRepository;
        private readonly ILogger<InventoryService> _logger;

        public InventoryService(
            IInventoryRepository inventoryRepository,
            IProductRepository productRepository,
            IBatchRepository batchRepository,
            ILogger<InventoryService> logger)
        {
            _inventoryRepository = inventoryRepository;
            _productRepository = productRepository;
            _batchRepository = batchRepository;
            _logger = logger;
        }

        public async Task<Inventory> AddInventoryAsync(Inventory inventory)
        {
            if (inventory.ProductID.HasValue && !await _productRepository.ExistsAsync(inventory.ProductID.Value))
                throw new ArgumentException("Указанный товар не существует");

            if (inventory.BatchID.HasValue && !await _batchRepository.ExistsAsync(inventory.BatchID.Value))
                throw new ArgumentException("Указанная партия не существует");

            if (inventory.Quantity < 0)
                throw new ArgumentException("Количество не может быть отрицательным");

            var createdInventory = await _inventoryRepository.CreateAsync(inventory);
            _logger.LogInformation("Добавлена складская позиция #{InventoryId} для товара #{ProductId}", 
                createdInventory.ID, inventory.ProductID);

            return createdInventory;
        }

        public async Task<bool> UpdateInventoryAsync(int id, int quantity)
        {
            if (quantity < 0)
                throw new ArgumentException("Количество не может быть отрицательным");

            var result = await _inventoryRepository.UpdateQuantityAsync(id, quantity);
            if (result)
            {
                _logger.LogInformation("Обновлено количество складской позиции #{InventoryId}: {Quantity}", id, quantity);
            }
            return result;
        }

        public async Task<bool> RemoveInventoryAsync(int id, int quantity)
        {
            if (quantity <= 0)
                throw new ArgumentException("Количество для удаления должно быть положительным");

            var inventory = await _inventoryRepository.GetByIdAsync(id);
            if (inventory == null)
                return false;

            if (inventory.Quantity < quantity)
                throw new InvalidOperationException("Недостаточно товара на складе");

            var newQuantity = inventory.Quantity - quantity;
            var result = await _inventoryRepository.UpdateQuantityAsync(id, newQuantity);
            
            if (result)
            {
                _logger.LogInformation("Удалено {Quantity} ед. товара со складской позиции #{InventoryId}", quantity, id);
            }
            return result;
        }

        public async Task<bool> TransferInventoryAsync(int fromId, int toId, int quantity)
        {
            if (quantity <= 0)
                throw new ArgumentException("Количество для переноса должно быть положительным");

            var result = await _inventoryRepository.TransferStockAsync(fromId, toId, quantity);
            if (result)
            {
                _logger.LogInformation("Перенесено {Quantity} ед. товара с позиции #{FromId} на позицию #{ToId}", 
                    quantity, fromId, toId);
            }
            return result;
        }

        public async Task<IEnumerable<Inventory>> GetLowStockItemsAsync(int threshold)
        {
            var lowStockItems = await _inventoryRepository.GetLowStockAsync(threshold);
            _logger.LogInformation("Найдено {Count} позиций с низким остатком (порог: {Threshold})", 
                lowStockItems.Count(), threshold);
            return lowStockItems;
        }

        public async Task<IEnumerable<Inventory>> GetExpiringItemsAsync(int daysThreshold)
        {
            var expiringItems = await _inventoryRepository.GetExpiringSoonAsync(daysThreshold);
            _logger.LogInformation("Найдено {Count} позиций с истекающим сроком годности (порог: {Days} дней)", 
                expiringItems.Count(), daysThreshold);
            return expiringItems;
        }

        public async Task<bool> ProcessBatchReceiptAsync(Batch batch, List<Inventory> inventoryItems)
        {
            using var transaction = await _inventoryRepository.BeginTransactionAsync();
            
            try
            {
                // Создание партии
                var createdBatch = await _batchRepository.CreateAsync(batch);

                // Создание складских позиций для партии
                foreach (var inventory in inventoryItems)
                {
                    inventory.BatchID = createdBatch.ID;
                    await _inventoryRepository.CreateAsync(inventory);
                }

                await transaction.CommitAsync();
                _logger.LogInformation("Обработана поставка #{BatchId} с {Count} позициями", 
                    createdBatch.ID, inventoryItems.Count);
                return true;
            }
            catch (Exception ex)
            {
                await transaction.RollbackAsync();
                _logger.LogError(ex, "Ошибка при обработке поставки");
                return false;
            }
        }

        public async Task<decimal> GetInventoryValueAsync()
        {
            var value = await _inventoryRepository.GetTotalValueAsync();
            _logger.LogInformation("Общая стоимость склада: {Value:C}", value);
            return value;
        }

        public async Task<int> GetTotalStockAsync()
        {
            var allInventory = await _inventoryRepository.GetAllAsync();
            var totalStock = allInventory.Sum(i => i.Quantity);
            _logger.LogInformation("Общее количество товара на складе: {Quantity}", totalStock);
            return totalStock;
        }

        public async Task<Dictionary<string, int>> GetStockByCategoryAsync()
        {
            var inventory = await _inventoryRepository.GetAllAsync();
            var stockByCategory = new Dictionary<string, int>();

            foreach (var item in inventory)
            {
                // В упрощенной схеме у Product нет навигационного свойства Category
                // Используем "Без категории" для всех товаров
                if (!stockByCategory.ContainsKey("Без категории"))
                    stockByCategory["Без категории"] = 0;
                stockByCategory["Без категории"] += item.Quantity;
            }

            return stockByCategory;
        }

        public async Task<bool> ValidateInventoryAvailabilityAsync(List<OrderItem> orderItems)
        {
            foreach (var item in orderItems)
            {
                if (item.ProductID.HasValue)
                {
                    var availableQuantity = await _inventoryRepository.GetTotalQuantityAsync(item.ProductID.Value);
                    if (availableQuantity < item.Quantity)
                    {
                        _logger.LogWarning("Недостаточно товара #{ProductId}: требуется {Required}, доступно {Available}", 
                            item.ProductID.Value, item.Quantity, availableQuantity);
                        return false;
                    }
                }
            }
            return true;
        }

        public async Task<bool> ReserveStockAsync(List<OrderItem> orderItems)
        {
            using var transaction = await _inventoryRepository.BeginTransactionAsync();
            
            try
            {
                foreach (var item in orderItems)
                {
                    if (item.ProductID.HasValue)
                    {
                        var inventoryItems = await _inventoryRepository.GetByProductAsync(item.ProductID.Value);
                        var remainingQuantity = item.Quantity;

                        foreach (var inventory in inventoryItems.Where(i => i.Quantity > 0))
                        {
                            if (remainingQuantity <= 0) break;

                            var reserveQuantity = Math.Min((byte)inventory.Quantity, (byte)remainingQuantity);
                            inventory.Quantity -= reserveQuantity;
                            await _inventoryRepository.UpdateAsync(inventory);
                            remainingQuantity -= reserveQuantity;
                        }

                        if (remainingQuantity > 0)
                            throw new InvalidOperationException($"Недостаточно товара на складе для резерва: {remainingQuantity}");
                    }
                }

                await transaction.CommitAsync();
                _logger.LogInformation("Зарезервировано товаров для {Count} позиций заказа", orderItems.Count);
                return true;
            }
            catch (Exception ex)
            {
                await transaction.RollbackAsync();
                _logger.LogError(ex, "Ошибка при резервировании товаров");
                return false;
            }
        }

        public async Task<bool> ReleaseStockAsync(List<OrderItem> orderItems)
        {
            using var transaction = await _inventoryRepository.BeginTransactionAsync();
            
            try
            {
                foreach (var item in orderItems)
                {
                    if (item.ProductID.HasValue)
                    {
                        var inventoryItems = await _inventoryRepository.GetByProductAsync(item.ProductID.Value);
                        if (inventoryItems.Any())
                        {
                            var firstInventory = inventoryItems.First();
                            firstInventory.Quantity += (item.Quantity ?? 0);
                            await _inventoryRepository.UpdateAsync(firstInventory);
                        }
                    }
                }

                await transaction.CommitAsync();
                _logger.LogInformation("Освобождено товаров для {Count} позиций заказа", orderItems.Count);
                return true;
            }
            catch (Exception ex)
            {
                await transaction.RollbackAsync();
                _logger.LogError(ex, "Ошибка при освобождении товаров");
                return false;
            }
        }

        public Task<bool> ConsumeStockAsync(List<OrderItem> orderItems)
        {
            // Товары уже зарезервированы, дополнительно ничего делать не нужно
            _logger.LogInformation("Списано товаров для {Count} позиций заказа", orderItems.Count);
            return Task.FromResult(true);
        }

        public async Task<Inventory?> GetProductInventoryAsync(int productId)
        {
            var inventoryItems = await _inventoryRepository.GetByProductAsync(productId);
            return inventoryItems.FirstOrDefault();
        }
    }
}