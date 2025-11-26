# Procure-to-Pay Backend

A Django REST Framework backend for a Procure-to-Pay system with multi-level approval workflow, document processing, and role-based access control.

## Features

- **JWT Authentication** with role-based permissions
- **Multi-level Approval Workflow** (Staff → Approver Level 1 → Approver Level 2 → Finance)
- **Document Processing** with OCR and PDF text extraction
- **Automatic Purchase Order Generation**
- **Receipt Validation** against purchase orders
- **File Upload Handling** for proformas, receipts, and POs
- **PostgreSQL Database** with Docker support
- **CORS Enabled** for frontend integration

## User Roles

1. **Staff** - Can create and manage their own purchase requests
2. **Approver Level 1** - Can approve first-level requests
3. **Approver Level 2** - Can approve second-level requests after Level 1 approval
4. **Finance** - Can view approved requests, upload receipts, and validate documents

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile

### Purchase Requests (Staff)
- `GET /api/requests/` - List user's requests
- `POST /api/requests/` - Create new request
- `GET /api/requests/{id}/` - Get request details
- `PUT /api/requests/{id}/` - Update pending request
- `POST /api/requests/{id}/upload-proforma/` - Upload proforma file
- `POST /api/requests/{id}/submit-receipt/` - Submit receipt (Finance only)

### Approvals
- `GET /api/approvals/pending/` - List requests pending approval
- `POST /api/requests/{id}/approve/` - Approve request
- `POST /api/requests/{id}/reject/` - Reject request

### Finance
- `GET /api/finance/approved-requests/` - List approved requests
- `GET /api/finance/purchase-orders/` - List generated POs
- `POST /api/finance/requests/{id}/validate-receipt/` - Validate receipt

### Document Processing
- `POST /api/documents/requests/{id}/extract-proforma/` - Extract data from proforma
- `POST /api/documents/requests/{id}/validate-receipt/` - Validate receipt against PO

## Setup Instructions

### Using Docker (Recommended)

1. **Clone the repository and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Start the services**
   ```bash
   docker-compose up --build
   ```

3. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin/

### Manual Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**
   - Create a database named `procure_pay`
   - Update database settings in `backend/settings.py`

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the server**
   ```bash
   python manage.py runserver
   ```

## Environment Variables

Create a `.env` file in the backend directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=procure_pay
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Workflow

1. **Staff** creates a purchase request with description, amount, and uploads proforma
2. **Approver Level 1** reviews and approves/rejects the request
3. **Approver Level 2** reviews approved requests from Level 1
4. Upon final approval, **Purchase Order** is automatically generated
5. **Finance** can upload receipts and validate them against the PO

## Document Processing

- **Proforma Extraction**: Uses pdfplumber and OCR to extract vendor, items, and pricing
- **PO Generation**: Creates PDF purchase orders using ReportLab
- **Receipt Validation**: Compares receipt data with PO for discrepancies

## Testing

```bash
python manage.py test
```

## Deployment

For production deployment:

1. Set `DEBUG=False`
2. Use a production-grade database
3. Set up proper static file serving
4. Configure HTTPS
5. Use environment variables for sensitive data

## Frontend Integration

The backend is designed to work with the React frontend. Make sure the frontend is configured to use the correct API base URL (http://localhost:8000 for development).

## License

This project is licensed under the MIT License.