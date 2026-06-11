# MeetMind Three-Tier Architecture - Updated README

![Architecture Diagram](https://img.shields.io/badge/Architecture-Three%20Tier-brightgreen)
![Status](https://img.shields.io/badge/Status-Production%20Ready-blue)


##  Project Overview

**MeetMind** is a modern three-tier web application that demonstrates enterprise-level DevOps practices on AWS. It showcases how to build, deploy, and scale a production-ready application across multiple architectural tiers.

###  Key Features

- **Tier 1 (Frontend)**: Global CDN with S3 + CloudFront for blazing-fast static asset delivery
- **Tier 2 (Application)**: Auto-scaling Flask API on Elastic Beanstalk behind ALB
- **Tier 3 (Database)**: Secure MongoDB in private subnet with encryption
- **Infrastructure as Code**: Complete Terraform configuration for reproducible deployments
- **CI/CD Ready**: GitHub Actions workflow for automated testing and deployment
- **Monitoring**: CloudWatch integration for metrics and alarms
- **Security**: VPC isolation, security groups, encrypted storage, environment-based secrets

##  Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        TIER 1: FRONTEND                     │
│                  ┌──────────────────────────┐               │
│                  │   CloudFront (CDN)       │               │
│                  │   - 200+ Edge Locations  │               │
│                  │   - SSL/TLS               │              │
│                  └─────────────┬────────────┘               │
│                                │                            │
└─────────────────────┬──────────┼───────────────┬────────────┘
                      │          │               │
                      ▼          ▼               ▼
            ┌────────────────┐  S3 Bucket   Origin Request
            │   Web Browser  │  (Static)
            └────────┬───────┘
                     │
                     │ HTTPS
                     │
        ┌────────────▼────────────────────────────────┐
        │   TIER 2: APPLICATION LAYER (AWS)           │
        │  ┌──────────────────────────────────────┐   │
        │  │  Application Load Balancer (ALB)     │   │
        │  │  - Distributes Traffic               │   │
        │  │  - Health Checks                     │   │
        │  └────────────────┬─────────────────────┘   │
        │                   │                         │
        │  ┌────────────────▼────────────────────┐    │
        │  │  Elastic Beanstalk (Auto-Scale)     │    │
        │  │  - Min: 2 instances                 │    │
        │  │  - Max: 6 instances                 │    │
        │  │  - Scale Trigger: CPU 30-70%        │    │
        │  │  - Python Flask Runtime             │    │
        │  └────────────────┬────────────────────┘    │
        │                   │                         │
        └───────────────────┼─────────────────────────┘
                            │
                   (Private Subnet)
                            │
        ┌───────────────────▼────────────────────┐
        │   TIER 3: DATABASE LAYER               │
        │  ┌──────────────────────────────────┐  │
        │  │  MongoDB EC2 (Private Subnet)    │  │
        │  │  - No Internet Access            │  │
        │  │  - Encrypted Storage (EBS gp3)   │  │
        │  │  - Auto Backups to S3            │  │
        │  │  - Port 27017 (App Only)         │  │
        │  └──────────────────────────────────┘  │
        └────────────────────────────────────────┘
```

##  Quick Start

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- Terraform >= 1.0
- Python 3.11+
- Docker & Docker Compose
- Git

### Local Development

```bash
# Clone repository
git clone https://github.com/ShantanuSambhare/MeetMind-two-tier-flask-app.git
cd MeetMind-two-tier-flask-app

# Setup local environment
chmod +x setup-local.sh
./setup-local.sh

# Run application
source venv/bin/activate
python app.py
```

Application will be available at `http://localhost:5000`

MongoDB Express UI: `http://localhost:8081` (admin/admin)

### AWS Deployment

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run automated deployment
./deploy.sh

# Or manual Terraform deployment
cd aws/terraform
terraform init
terraform plan
terraform apply
```

For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

##  API Endpoints

### Health Check
```bash
GET /health
# Response: {"status": "healthy", "service": "MeetMind API", "environment": "production"}
```

### Employees
```bash
# Create employee
POST /api/employees
{
  "name": "John Doe",
  "role": "Software Engineer",
  "department": "Engineering",
  "email": "john@example.com",
  "message": "Optional message"
}

# Get all employees
GET /api/employees

# Delete employee
DELETE /api/employees/{id}
```

### Meetings
```bash
# Create meeting
POST /api/meetings
{
  "title": "Sprint Planning",
  "notes": "Discuss Q1 roadmap",
  "action_items": "Finalize backlog"
}

# Get all meetings
GET /api/meetings

# Delete meeting
DELETE /api/meetings/{id}
```

##  Configuration

### Environment Variables
```bash
# Database
MONGODB_URI=mongodb://admin:password@host:27017/meetmind?authSource=admin

# Application
ENVIRONMENT=production          # production or development
FLASK_ENV=production
PORT=5000

# AWS
AWS_REGION=us-east-1
S3_BUCKET=meetmind-static-assets-xxxxx
CLOUDFRONT_DOMAIN=d1234567890abc.cloudfront.net
```

Set these in Elastic Beanstalk environment configuration.

##  Monitoring & Logs

### CloudWatch Logs
```bash
# View application logs
aws logs tail /aws/elasticbeanstalk/meetmind-env/var/log/eb-engine.log --follow

# View MongoDB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-xxxxx \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

### Application Monitoring
- **ALB Health Check**: `/health` endpoint (30 second interval)
- **Auto-Scaling**: Triggers at CPU > 70% (scale up) or < 30% (scale down)
- **Database Alarms**: CPU > 80%, Storage > 85%

##  Security Features

 **Network Security**
- VPC with public/private subnets
- Internet Gateway for public access
- NAT Gateway for private subnet internet access
- Security groups restrict traffic between tiers

 **Data Security**
- MongoDB in private subnet (not exposed to internet)
- EBS volumes encrypted with AWS KMS
- Database authentication required
- Environment variables for secrets (not committed to Git)

 **Access Control**
- IAM roles for EC2 instances
- Application Load Balancer health checks
- CloudFront origin access identity

##  Scalability

### Auto-Scaling Configuration
```hcl
Min Instances: 2              # Always running 2 for HA
Max Instances: 6              # Cost control
Scale Up Trigger: CPU > 70%
Scale Down Trigger: CPU < 30%
Cool Down Period: 300 seconds # Prevent flapping
```

### Performance Metrics
- **Frontend**: CloudFront edge caching (edge latency < 100ms)
- **Application**: ALB request routing (< 10ms)
- **Database**: MongoDB indexes for query optimization

##  Cost Optimization

### Estimated Monthly Costs (US-East-1)
| Component | Instance Type | Count | Cost/Month |
|-----------|---------------|-------|-----------|
| Elastic Beanstalk | t3.small | 2-6 | $25-75 |
| MongoDB | t3.medium | 1 | $30 |
| NAT Gateway | - | 1 | $32 |
| CloudFront | - | - | $0.085/GB |
| S3 | - | - | $0.023/GB |
| **Total** | | | **~$90-200** |

### Cost Reduction Tips
1. Use Spot Instances (30% cheaper) - requires fault tolerance
2. Right-size instances based on metrics
3. Enable S3 Intelligent Tiering
4. Set CloudFront TTL appropriately

##  Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Step-by-step deployment instructions
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture decisions and rationale
- [Terraform Docs](aws/terraform/README.md) - Infrastructure as Code details

##  CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/deploy.yml`):
1. **Test**: Run unit tests with MongoDB
2. **Build**: Build Docker image and push to registry
3. **Deploy**: Deploy to Elastic Beanstalk
4. **Smoke Test**: Verify deployment health

Trigger: Push to `main` branch

##  Development

### Project Structure
```
.
├── app.py                          # Flask application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container image
├── docker-compose.yml              # Local development
├── .env.example                    # Environment variables template
├── init-mongo.js                   # MongoDB initialization
├── DEPLOYMENT_GUIDE.md             # Deployment documentation
├── ARCHITECTURE.md                 # Architecture decisions
├── deploy.sh                       # Automated deployment script
├── setup-local.sh                  # Local setup script
├── aws/
│   └── terraform/
│       ├── main.tf                 # VPC and networking
│       ├── beanstalk.tf            # Elastic Beanstalk config
│       ├── mongodb.tf              # MongoDB EC2 config
│       ├── variables.tf            # Variables definition
│       ├── terraform.tfvars        # Variables values
│       └── mongodb-install.sh      # MongoDB installation
└── .github/
    └── workflows/
        └── deploy.yml              # CI/CD pipeline
```

##  Troubleshooting

### Application can't connect to MongoDB
```bash
# Check security group allows port 27017
aws ec2 describe-security-groups --group-ids sg-xxxxx

# SSH to Beanstalk instance and test connection
telnet 10.0.10.x 27017
```

### High Latency to Database
- Ensure Beanstalk and MongoDB are in same VPC
- Check EC2 instance CPU and network performance
- Verify MongoDB indexes

### Application not responding
```bash
# Check ALB target health
aws elbv2 describe-target-health --target-group-arn arn:aws:...

# View Beanstalk logs
eb logs

# SSH to instance and check Flask process
ps aux | grep python
```

##  Learning Resources

- [AWS Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [AWS VPC Best Practices](https://docs.aws.amazon.com/vpc/latest/userguide/)
- [Flask Documentation](https://flask.palletsprojects.com/)

##  License

This project is licensed under the MIT License - see LICENSE file for details.

##  Author

**Shantanu Sambhare**
- GitHub: [@ShantanuSambhare](https://github.com/ShantanuSambhare)
- Project: [MeetMind Three-Tier App](https://github.com/ShantanuSambhare/MeetMind-two-tier-flask-app)

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

##  Support

For issues and questions, please create an issue on GitHub or contact the author.

---

**Last Updated**: 2024
**Status**: Production Ready ✅
