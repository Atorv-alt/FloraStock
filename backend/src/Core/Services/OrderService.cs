using Core.Interfaces;
using Shared.Entities;
using Microsoft.Extensions.Logging;

namespace Core.Services
{
    public class OrderService : IOrderService
    {
        private readonly IOrderRepository _orderRepository;
        private readonly IInventoryRepository _inventoryRepository;
        private readonly IProductRepository _productRepository;
        private readonly ILogger<OrderService> _logger;

        public OrderService(
            IOrderRepository orderRepository,
            IInventoryRepository inventoryRepository,
            IProductRepository productRepository,
            ILogger<OrderService> logger)
        {
            _orderRepository = orderRepository;
            _inventoryRepository = inventoryRepository;
            _productRepository = productRepository;
            _logger = logger;
        }

        public async Task<Order> CreateOrderAsync(Order order, List<OrderItem> orderItems)
        {
            using var transaction = await _orderRepository.BeginTransactionAsync();
            
            try
            {
                // Проверка доступности товаров на складе
                if (!await CheckInventoryAsync(orderItems))
                {
                    throw new InvalidOperationException("Недостаточно товаров на складе");
                }

                // Создание заказа
                order.TotalAmount = await CalculateOrderTotalAsync(orderItems);
                var createdOrder = await _orderRepository.CreateAsync(order);

                // Создание позиций заказа
                foreach (var item in orderItems)
                {
                    item.OrderID = createdOrder.ID;
                    item.UnitPrice = await GetProductPriceAsync(item.ProductID!.Value);
                    await _orderRepository.CreateOrderItemAsync(item);
                }

                // Резервирование товаров на складе
                await ReserveInventoryAsync(orderItems);

                await transaction.CommitAsync();
                _logger.LogInformation("Создан заказ #{OrderId} на сумму {TotalAmount}", createdOrder.ID, createdOrder.TotalAmount);
                
                return createdOrder;
            }
            catch (Exception ex)
            {
                await transaction.RollbackAsync();
                _logger.LogError(ex, "Ошибка при создании заказа");
                throw;
            }
        }

        public async Task<Order> UpdateOrderAsync(Order order)
        {
            var existingOrder = await _orderRepository.GetByIdAsync(order.ID);
            if (existingOrder == null)
                throw new KeyNotFoundException($"Заказ с ID {order.ID} не найден");

            var updatedOrder = await _orderRepository.UpdateAsync(order);
            
            _logger.LogInformation("Обновлен заказ #{OrderId}", order.ID);
            return updatedOrder;
        }

        public async Task<bool> CancelOrderAsync(int orderId)
        {
            var order = await _orderRepository.GetByIdAsync(orderId);
            if (order == null)
                return false;

            if (order.Status != "Новый" && order.Status != "В обработке")
                throw new InvalidOperationException("Нельзя отменить заказ в текущем статусе");

            // Освобождение зарезервированных товаров
            var orderItems = await _orderRepository.GetOrderItemsAsync(orderId);
            await ReleaseInventoryAsync(orderItems.ToList());

            // Допустимые статусы: Новый, В обработке, Выполнен, Доставлен
            // (статуса "Отменен" нет), поэтому отмена = удаление заказа вместе с позициями.
            var cancelled = await _orderRepository.DeleteOrderWithItemsAsync(orderId);
            if (cancelled)
                _logger.LogInformation("Заказ #{OrderId} отменен", orderId);
            return cancelled;
        }

        public async Task<bool> AddOrderItemAsync(int orderId, OrderItem orderItem)
        {
            var order = await _orderRepository.GetByIdAsync(orderId);
            if (order == null)
                return false;

            if (order.Status != "Новый" && order.Status != "В обработке")
                throw new InvalidOperationException("Нельзя изменить заказ в текущем статусе");

            // Проверка доступности товара
            var availableQuantity = await _inventoryRepository.GetTotalQuantityAsync(orderItem.ProductID!.Value);
            if (availableQuantity < (orderItem.Quantity ?? 0))
                throw new InvalidOperationException("Недостаточно товара на складе");

            orderItem.OrderID = orderId;
            orderItem.UnitPrice = await GetProductPriceAsync(orderItem.ProductID.Value);
            
            await _orderRepository.CreateOrderItemAsync(orderItem);
            await ReserveInventoryAsync(new List<OrderItem> { orderItem });

            // Обновление общей суммы заказа
            order.TotalAmount = await CalculateOrderTotalAsync(orderId);
            await _orderRepository.UpdateAsync(order);

            _logger.LogInformation("Добавлена позиция к заказу #{OrderId}", orderId);
            return true;
        }

        public async Task<bool> RemoveOrderItemAsync(int orderId, int productId)
        {
            var order = await _orderRepository.GetByIdAsync(orderId);
            if (order == null)
                return false;

            if (order.Status != "Новый" && order.Status != "В обработке")
                throw new InvalidOperationException("Нельзя изменить заказ в текущем статусе");

            var orderItem = await _orderRepository.GetOrderItemAsync(orderId, productId);
            if (orderItem == null)
                return false;

            await _orderRepository.DeleteOrderItemAsync(orderItem.ID);
            await ReleaseInventoryAsync(new List<OrderItem> { orderItem });

            // Обновление общей суммы заказа
            order.TotalAmount = await CalculateOrderTotalAsync(orderId);
            await _orderRepository.UpdateAsync(order);

            _logger.LogInformation("Удалена позиция из заказа #{OrderId}", orderId);
            return true;
        }

        public async Task<bool> UpdateOrderItemAsync(int orderId, int productId, int quantity, decimal unitPrice)
        {
            var order = await _orderRepository.GetByIdAsync(orderId);
            if (order == null)
                return false;

            if (order.Status != "Новый" && order.Status != "В обработке")
                throw new InvalidOperationException("Нельзя изменить заказ в текущем статусе");

            var orderItem = await _orderRepository.GetOrderItemAsync(orderId, productId);
            if (orderItem == null)
                return false;

            var quantityDifference = quantity - orderItem.Quantity;

            // Проверка доступности товара при увеличении количества
            if (quantityDifference > 0)
            {
                var availableQuantity = await _inventoryRepository.GetTotalQuantityAsync(productId);
                if (availableQuantity < quantityDifference)
                    throw new InvalidOperationException("Недостаточно товара на складе");
            }

            // Освобождение старого количества и резервирование нового
            var oldItem = new OrderItem { ProductID = productId, Quantity = orderItem.Quantity };
            await ReleaseInventoryAsync(new List<OrderItem> { oldItem });

            orderItem.Quantity = quantity;
            orderItem.UnitPrice = unitPrice;
            
            await _orderRepository.UpdateOrderItemAsync(orderItem);
            await ReserveInventoryAsync(new List<OrderItem> { orderItem });

            // Обновление общей суммы заказа
            order.TotalAmount = await CalculateOrderTotalAsync(orderId);
            await _orderRepository.UpdateAsync(order);

            _logger.LogInformation("Обновлена позиция в заказе #{OrderId}", orderId);
            return true;
        }

        public async Task<bool> ProcessOrderAsync(int orderId)
        {
            var order = await _orderRepository.GetByIdAsync(orderId);
            if (order == null)
                return false;

            if (order.Status != "Новый")
                throw new InvalidOperationException("Заказ уже в обработке");

            order.Status = "В обработке";
            await _orderRepository.UpdateAsync(order);

            _logger.LogInformation("Заказ #{OrderId} передан в обработку", orderId);
            return true;
        }

        public async Task<bool> CompleteOrderAsync(int orderId)
        {
            var order = await _orderRepository.GetByIdAsync(orderId);
            if (order == null)
                return false;

            if (order.Status != "В обработке")
                throw new InvalidOperationException("Заказ не находится в обработке");

            // Списание товаров со склада
            var orderItems = await _orderRepository.GetOrderItemsAsync(orderId);
            await ConsumeInventoryAsync(orderItems.ToList());

            order.Status = "Выполнен";
            await _orderRepository.UpdateAsync(order);

            _logger.LogInformation("Заказ #{OrderId} выполнен", orderId);
            return true;
        }

        public async Task<decimal> CalculateOrderTotalAsync(int orderId)
        {
            var orderItems = await _orderRepository.GetOrderItemsAsync(orderId);
            return orderItems.Sum(item => (item.Quantity ?? 0) * (item.UnitPrice ?? 0));
        }

        public async Task<decimal> CalculateOrderTotalAsync(List<OrderItem> orderItems)
        {
            decimal total = 0;
            foreach (var item in orderItems)
            {
                item.UnitPrice = await GetProductPriceAsync(item.ProductID!.Value);
                total += (item.Quantity ?? 0) * (item.UnitPrice ?? 0);
            }
            return total;
        }

        public async Task<bool> CheckInventoryAsync(List<OrderItem> orderItems)
        {
            foreach (var item in orderItems)
            {
                if (item.ProductID.HasValue)
                {
                    var availableQuantity = await _inventoryRepository.GetTotalQuantityAsync(item.ProductID.Value);
                    if (availableQuantity < (item.Quantity ?? 0))
                        return false;
                }
            }
            return true;
        }

        public async Task<bool> ReserveInventoryAsync(List<OrderItem> orderItems)
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

                        var reserveQuantity = Math.Min(inventory.Quantity, remainingQuantity ?? 0);
                        inventory.Quantity -= reserveQuantity;
                        await _inventoryRepository.UpdateAsync(inventory);
                        remainingQuantity -= reserveQuantity;
                    }

                    if (remainingQuantity > 0)
                        throw new InvalidOperationException($"Недостаточно товара на складе для резерва: {remainingQuantity}");
                }
            }
            return true;
        }

        public async Task<bool> ReleaseInventoryAsync(List<OrderItem> orderItems)
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
            return true;
        }

        public Task<bool> ConsumeInventoryAsync(List<OrderItem> orderItems)
        {
            // Товары уже зарезервированы, дополнительно ничего делать не нужно
            return Task.FromResult(true);
        }

        public async Task<IEnumerable<Order>> GetOrdersByStatusAsync(string status)
        {
            return await _orderRepository.GetByStatusAsync(status);
        }

        public async Task<IEnumerable<Order>> GetPendingOrdersAsync()
        {
            return await _orderRepository.GetByStatusAsync("Новый");
        }

        public async Task<Order?> GetOrderWithItemsAsync(int orderId)
        {
            return await _orderRepository.GetByIdAsync(orderId);
        }

        private async Task<decimal> GetProductPriceAsync(int productId)
        {
            var product = await _productRepository.GetByIdAsync(productId);
            return product?.RetailPrice ?? 0;
        }
    }
}