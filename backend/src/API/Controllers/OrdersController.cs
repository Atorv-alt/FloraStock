using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Core.Interfaces;
using Shared.Entities;
using API.DTOs;

namespace API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class OrdersController : ControllerBase
    {
        private readonly IOrderRepository _orderRepository;
        private readonly IClientRepository _clientRepository;
        private readonly IEmployeeRepository _employeeRepository;
        private readonly IProductRepository _productRepository;
        private readonly ILogger<OrdersController> _logger;

        public OrdersController(
            IOrderRepository orderRepository,
            IClientRepository clientRepository,
            IEmployeeRepository employeeRepository,
            IProductRepository productRepository,
            ILogger<OrdersController> logger)
        {
            _orderRepository = orderRepository;
            _clientRepository = clientRepository;
            _employeeRepository = employeeRepository;
            _productRepository = productRepository;
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<OrderDto>>> GetAll()
        {
            try
            {
                var orders = await _orderRepository.GetAllAsync();
                var clients = await _clientRepository.GetAllAsync();
                var employees = await _employeeRepository.GetAllAsync();
                
                var orderDtos = new List<OrderDto>();
                
                foreach (var order in orders)
                {
                    var client = clients.FirstOrDefault(c => c.ID == order.ClientID);
                    var employee = employees.FirstOrDefault(e => e.ID == order.EmployeeID);
                    
                    orderDtos.Add(OrderDto.FromOrder(order, client, employee));
                }
                
                return Ok(orderDtos);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении заказов");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Order>> GetById(int id)
        {
            try
            {
                var order = await _orderRepository.GetByIdAsync(id);
                if (order == null)
                {
                    return NotFound(new { message = "Заказ не найден" });
                }

                return Ok(order);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении заказа с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("status/{status}")]
        public async Task<ActionResult<IEnumerable<Order>>> GetByStatus(string status)
        {
            try
            {
                var orders = await _orderRepository.GetByStatusAsync(status);
                return Ok(orders);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении заказов по статусу: {Status}", status);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("client/{clientId}")]
        public async Task<ActionResult<IEnumerable<Order>>> GetByClient(int clientId)
        {
            try
            {
                if (!await _clientRepository.ExistsAsync(clientId))
                {
                    return NotFound(new { message = "Клиент не найден" });
                }

                var orders = await _orderRepository.GetByClientAsync(clientId);
                return Ok(orders);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении заказов клиента");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("date-range")]
        public async Task<ActionResult<IEnumerable<Order>>> GetByDateRange([FromQuery] DateTime startDate, [FromQuery] DateTime endDate)
        {
            try
            {
                var orders = await _orderRepository.GetByDateRangeAsync(NormalizeToUtc(startDate), NormalizeToUtc(endDate));
                return Ok(orders);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении заказов за период");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPost]
        public async Task<ActionResult<Order>> Create([FromBody] CreateOrderRequest request)
        {
            try
            {
                if (request.ClientId.HasValue && !await _clientRepository.ExistsAsync(request.ClientId.Value))
                {
                    return BadRequest(new { message = "Указанный клиент не существует" });
                }

                if (request.EmployeeId.HasValue && !await _employeeRepository.ExistsAsync(request.EmployeeId.Value))
                {
                    return BadRequest(new { message = "Указанный сотрудник не существует" });
                }

                if (string.IsNullOrEmpty(request.OrderNumber))
                {
                    request.OrderNumber = await GenerateOrderNumberAsync();
                }
                else if (await _orderRepository.OrderNumberExistsAsync(request.OrderNumber))
                {
                    return Conflict(new { message = "Заказ с таким номером уже существует" });
                }

                var order = new Order
                {
                    ClientId = request.ClientId,
                    EmployeeId = request.EmployeeId,
                    OrderNumber = request.OrderNumber,
                    OrderDate = NormalizeToUtc(request.OrderDate?.Date) ?? DateTime.SpecifyKind(DateTime.Today, DateTimeKind.Utc),
                    Status = request.Status ?? "Новый",
                    TotalAmount = request.TotalAmount
                };

                var createdOrder = await _orderRepository.CreateAsync(order);
                return CreatedAtAction(nameof(GetById), new { id = createdOrder.ID }, createdOrder);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при создании заказа");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPut("{id}")]
        public async Task<ActionResult<Order>> Update(int id, [FromBody] UpdateOrderRequest request)
        {
            try
            {
                var existingOrder = await _orderRepository.GetByIdAsync(id);
                if (existingOrder == null)
                {
                    return NotFound(new { message = "Заказ не найден" });
                }

                if (request.ClientId.HasValue && !await _clientRepository.ExistsAsync(request.ClientId.Value))
                {
                    return BadRequest(new { message = "Указанный клиент не существует" });
                }

                if (request.EmployeeId.HasValue && !await _employeeRepository.ExistsAsync(request.EmployeeId.Value))
                {
                    return BadRequest(new { message = "Указанный сотрудник не существует" });
                }

                if (!string.IsNullOrEmpty(request.OrderNumber) && 
                    request.OrderNumber != existingOrder.OrderNumber &&
                    await _orderRepository.OrderNumberExistsAsync(request.OrderNumber, id))
                {
                    return Conflict(new { message = "Заказ с таким номером уже существует" });
                }

                existingOrder.ClientId = request.ClientId;
                existingOrder.EmployeeId = request.EmployeeId;
                existingOrder.OrderNumber = request.OrderNumber ?? existingOrder.OrderNumber;
                existingOrder.OrderDate = NormalizeToUtc(request.OrderDate?.Date) ?? NormalizeToUtc(existingOrder.OrderDate);
                existingOrder.Status = request.Status ?? existingOrder.Status;
                existingOrder.TotalAmount = request.TotalAmount ?? existingOrder.TotalAmount;

                var updatedOrder = await _orderRepository.UpdateAsync(existingOrder);
                return Ok(updatedOrder);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при обновлении заказа с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpDelete("{id}")]
        public async Task<ActionResult> Delete(int id)
        {
            try
            {
                if (!await _orderRepository.ExistsAsync(id))
                {
                    return NotFound(new { message = "Заказ не найден" });
                }

                var result = await _orderRepository.DeleteOrderWithItemsAsync(id);
                if (!result)
                {
                    return BadRequest(new { message = "Не удалось удалить заказ" });
                }

                return NoContent();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при удалении заказа с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("revenue")]
        public async Task<ActionResult<decimal>> GetRevenue([FromQuery] DateTime? startDate, [FromQuery] DateTime? endDate)
        {
            try
            {
                var revenue = await _orderRepository.GetTotalRevenueAsync(NormalizeToUtc(startDate), NormalizeToUtc(endDate));
                return Ok(revenue);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при расчете выручки");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("count")]
        public async Task<ActionResult<int>> GetCount([FromQuery] DateTime? startDate, [FromQuery] DateTime? endDate)
        {
            try
            {
                var count = await _orderRepository.GetTotalOrdersAsync(NormalizeToUtc(startDate), NormalizeToUtc(endDate));
                return Ok(count);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при подсчете заказов");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        private static DateTime NormalizeToUtc(DateTime value)
        {
            return value.Kind switch
            {
                DateTimeKind.Utc => value,
                DateTimeKind.Local => value.ToUniversalTime(),
                // Дата без зоны (напр. "2026-09-27" из календаря) — это локальная дата
                _ => DateTime.SpecifyKind(value, DateTimeKind.Local).ToUniversalTime(),
            };
        }

        private static DateTime? NormalizeToUtc(DateTime? value)
        {
            return value.HasValue ? NormalizeToUtc(value.Value) : null;
        }

        private async Task<string> GenerateOrderNumberAsync()
        {
            // Формат ORD-XXX/ГГГГ (совместим с валидацией клиента и CHECK в БД)
            var year = DateTime.Now.Year;
            var total = await _orderRepository.GetTotalOrdersAsync();
            var number = (int)total + 1;
            string candidate;
            do
            {
                candidate = $"ORD-{number:D3}/{year}";
                number++;
            } while (await _orderRepository.OrderNumberExistsAsync(candidate));
            return candidate;
        }
    }

    public class CreateOrderRequest
    {
        public int? ClientId { get; set; }
        public int? EmployeeId { get; set; }
        public string? OrderNumber { get; set; }
        public DateTime? OrderDate { get; set; }
        public string? Status { get; set; }
        public decimal TotalAmount { get; set; }
    }

    public class UpdateOrderRequest
    {
        public int? ClientId { get; set; }
        public int? EmployeeId { get; set; }
        public string? OrderNumber { get; set; }
        public DateTime? OrderDate { get; set; }
        public string? Status { get; set; }
        public decimal? TotalAmount { get; set; }
        public bool? IsActive { get; set; }
    }
}