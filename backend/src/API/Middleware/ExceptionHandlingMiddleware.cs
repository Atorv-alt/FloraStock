using System.Net;
using System.Text.Json;
using Microsoft.AspNetCore.Mvc;

namespace API.Middleware
{
    public class ExceptionHandlingMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly ILogger<ExceptionHandlingMiddleware> _logger;

        public ExceptionHandlingMiddleware(RequestDelegate next, ILogger<ExceptionHandlingMiddleware> logger)
        {
            _next = next;
            _logger = logger;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            try
            {
                await _next(context);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Произошло необработанное исключение");
                await HandleExceptionAsync(context, ex);
            }
        }

        private static async Task HandleExceptionAsync(HttpContext context, Exception exception)
        {
            context.Response.Clear();
            context.Response.ContentType = "application/json";
            
            var response = exception switch
            {
                ArgumentException => CreateErrorResponse("Неверные аргументы", exception.Message, HttpStatusCode.BadRequest),
                UnauthorizedAccessException => CreateErrorResponse("Доступ запрещен", exception.Message, HttpStatusCode.Unauthorized),
                KeyNotFoundException => CreateErrorResponse("Ресурс не найден", exception.Message, HttpStatusCode.NotFound),
                InvalidOperationException => CreateErrorResponse("Недопустимая операция", exception.Message, HttpStatusCode.BadRequest),
                TimeoutException => CreateErrorResponse("Таймаут операции", exception.Message, HttpStatusCode.RequestTimeout),
                _ => CreateErrorResponse("Внутренняя ошибка сервера", "Произошла непредвиденная ошибка", HttpStatusCode.InternalServerError)
            };

            context.Response.StatusCode = (int)response.StatusCode;
            
            var jsonOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                WriteIndented = true
            };

            var jsonResponse = JsonSerializer.Serialize(response, jsonOptions);
            await context.Response.WriteAsync(jsonResponse);
        }

        private static ErrorResponse CreateErrorResponse(string title, string message, HttpStatusCode statusCode)
        {
            return new ErrorResponse
            {
                Title = title,
                Message = message,
                StatusCode = (int)statusCode,
                Timestamp = DateTime.UtcNow,
                Path = "" // Will be filled by the middleware
            };
        }
    }

    public class ErrorResponse
    {
        public string Title { get; set; } = string.Empty;
        public string Message { get; set; } = string.Empty;
        public int StatusCode { get; set; }
        public DateTime Timestamp { get; set; }
        public string Path { get; set; } = string.Empty;
        public List<ValidationError>? Errors { get; set; }
    }

    public class ValidationError
    {
        public string Field { get; set; } = string.Empty;
        public string Message { get; set; } = string.Empty;
    }
}