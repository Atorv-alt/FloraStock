using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Core.Interfaces;
using Shared.Entities;

namespace API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class ClientsController : ControllerBase
    {
        private readonly IClientRepository _clientRepository;
        private readonly ILogger<ClientsController> _logger;

        public ClientsController(
            IClientRepository clientRepository,
            ILogger<ClientsController> logger)
        {
            _clientRepository = clientRepository;
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<Client>>> GetAll()
        {
            try
            {
                var clients = await _clientRepository.GetAllAsync();
                return Ok(clients);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении клиентов");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("active")]
        public async Task<ActionResult<IEnumerable<Client>>> GetActive()
        {
            try
            {
                var clients = await _clientRepository.GetActiveAsync();
                return Ok(clients);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении активных клиентов");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Client>> GetById(int id)
        {
            try
            {
                var client = await _clientRepository.GetByIdAsync(id);
                if (client == null)
                {
                    return NotFound(new { message = "Клиент не найден" });
                }

                return Ok(client);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при получении клиента с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("search/phone/{phoneNumber}")]
        public async Task<ActionResult<Client>> GetByPhone(string phoneNumber)
        {
            try
            {
                var client = await _clientRepository.GetByPhoneAsync(phoneNumber);
                if (client == null)
                {
                    return NotFound(new { message = "Клиент с таким номером телефона не найден" });
                }

                return Ok(client);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при поиске клиента по номеру телефона");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpGet("search/email/{email}")]
        public async Task<ActionResult<Client>> GetByEmail(string email)
        {
            try
            {
                var client = await _clientRepository.GetByEmailAsync(email);
                if (client == null)
                {
                    return NotFound(new { message = "Клиент с таким email не найден" });
                }

                return Ok(client);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при поиске клиента по email");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPost]
        public async Task<ActionResult<Client>> Create([FromBody] CreateClientRequest request)
        {
            try
            {
                if (string.IsNullOrEmpty(request.FullName))
                {
                    return BadRequest(new { message = "ФИО клиента обязательно" });
                }

                if (!string.IsNullOrEmpty(request.PhoneNumber) && 
                    await _clientRepository.PhoneExistsAsync(request.PhoneNumber))
                {
                    return Conflict(new { message = "Клиент с таким номером телефона уже существует" });
                }

                if (!string.IsNullOrEmpty(request.Email) && 
                    await _clientRepository.EmailExistsAsync(request.Email))
                {
                    return Conflict(new { message = "Клиент с таким email уже существует" });
                }

                var client = new Client
                {
                    FullName = request.FullName,
                    PhoneNumber = request.PhoneNumber,
                    Email = request.Email
                };

                var createdClient = await _clientRepository.CreateAsync(client);
                return CreatedAtAction(nameof(GetById), new { ID = createdClient.ID }, createdClient);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при создании клиента");
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpPut("{id}")]
        public async Task<ActionResult<Client>> Update(int id, [FromBody] UpdateClientRequest request)
        {
            try
            {
                var existingClient = await _clientRepository.GetByIdAsync(id);
                if (existingClient == null)
                {
                    return NotFound(new { message = "Клиент не найден" });
                }

                if (string.IsNullOrEmpty(request.FullName))
                {
                    return BadRequest(new { message = "ФИО клиента обязательно" });
                }

                if (!string.IsNullOrEmpty(request.PhoneNumber) && 
                    await _clientRepository.PhoneExistsAsync(request.PhoneNumber, id))
                {
                    return Conflict(new { message = "Клиент с таким номером телефона уже существует" });
                }

                if (!string.IsNullOrEmpty(request.Email) && 
                    await _clientRepository.EmailExistsAsync(request.Email, id))
                {
                    return Conflict(new { message = "Клиент с таким email уже существует" });
                }

                existingClient.FullName = request.FullName;
                existingClient.PhoneNumber = request.PhoneNumber;
                existingClient.Email = request.Email;

                var updatedClient = await _clientRepository.UpdateAsync(existingClient);
                return Ok(updatedClient);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при обновлении клиента с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }

        [HttpDelete("{id}")]
        public async Task<ActionResult> Delete(int id)
        {
            try
            {
                if (!await _clientRepository.ExistsAsync(id))
                {
                    return NotFound(new { message = "Клиент не найден" });
                }

                var result = await _clientRepository.DeleteAsync(id);
                if (!result)
                {
                    return BadRequest(new { message = "Не удалось удалить клиента" });
                }

                return NoContent();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Ошибка при удалении клиента с ID: {Id}", id);
                return StatusCode(500, new { message = "Внутренняя ошибка сервера" });
            }
        }
    }

    public class CreateClientRequest
    {
        public string FullName { get; set; } = string.Empty;
        public string? PhoneNumber { get; set; }
        public string? Email { get; set; }
    }

    public class UpdateClientRequest
    {
        public string FullName { get; set; } = string.Empty;
        public string? PhoneNumber { get; set; }
        public string? Email { get; set; }
        public bool IsActive { get; set; } = true;
    }
}