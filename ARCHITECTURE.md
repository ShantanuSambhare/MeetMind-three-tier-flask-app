# Architecture Decision Records (ADR) for MeetMind Three-Tier Deployment

## ADR 1: Why Use Elastic Beanstalk for Application Layer?

### Context
Need to deploy Flask application on AWS with auto-scaling capabilities.

### Decision
Use AWS Elastic Beanstalk instead of bare EC2 instances or ECS.

### Rationale
1. **Managed Service**: Handles deployment, scaling, and health monitoring automatically
2. **Easy CI/CD Integration**: Seamless integration with AWS CodePipeline
3. **Environment Management**: Simple management of staging/production environments
4. **Automatic Scaling**: Built-in auto-scaling based on metrics
5. **Cost-Effective**: Pay for compute only, no additional fees for the platform
6. **Python Support**: Native support for Python applications

### Alternatives Considered
- **ECS (Docker)**: More complex, requires more management
- **EKS (Kubernetes)**: Overkill for this use case, steeper learning curve
- **Lambda**: Not suitable for long-running Flask applications
- **Bare EC2**: Requires manual scaling and deployment setup

---

## ADR 2: Why S3 + CloudFront for Frontend Instead of EC2 + Nginx?

### Context
Need to serve static frontend assets efficiently.

### Decision
Use S3 for storage and CloudFront for CDN delivery instead of Nginx on EC2.

### Rationale
1. **Cost**: S3 + CloudFront is ~60% cheaper than EC2 + Nginx
2. **Availability**: 99.99% uptime SLA vs managing servers
3. **Scalability**: Automatically scales to handle traffic spikes
4. **CDN**: CloudFront provides global edge locations (200+ PoP)
5. **Security**: Built-in DDoS protection with AWS Shield
6. **Maintenance**: No patching or server management required
7. **Performance**: Edge caching provides sub-100ms latency globally

### Alternative: Nginx on EC2
- Pros: Full control, can serve dynamic content
- Cons: Manual scaling, requires maintenance, higher latency, higher cost

### Choice Summary
**S3 + CloudFront** provides the best balance of cost, performance, and maintainability for static frontend assets.

---

## ADR 3: MongoDB on EC2 Private Subnet Instead of Amazon DocumentDB?

### Context
Need NoSQL database for flexible data model. Choosing between managed service and self-hosted.

### Decision
Use MongoDB on EC2 in private subnet (with option to migrate to DocumentDB later).

### Rationale
1. **Cost**: EC2 MongoDB ~50% cheaper than DocumentDB
2. **Control**: Full control over configurations, indexes, and optimization
3. **Learning**: Hands-on DevOps experience (educational value)
4. **Flexibility**: Can install additional tools and monitoring
5. **Private Subnet**: Secure, not exposed to internet
6. **Migration Path**: Can migrate to DocumentDB later without code changes

### Advantages of This Approach
- Security: Private subnet + Security Group access
- Backup: Can implement custom backup strategies
- Monitoring: Full access to logs and metrics
- Cost: Predictable, lower cost than managed services

### Why Not DocumentDB?
- Higher cost (~2x more expensive)
- Overkill for current application size
- MongoDB knowledge is more portable

### Future Consideration
Can migrate to DocumentDB for hands-off management when scaling up.

---

## ADR 4: Three-Tier Architecture vs Two-Tier?

### Context
Deciding on architecture layers for separation of concerns.

### Decision
Use Three-Tier Architecture:
- **Tier 1**: Frontend (S3 + CloudFront)
- **Tier 2**: Application (Beanstalk + ALB)
- **Tier 3**: Database (MongoDB on EC2 Private)

### Rationale for Three-Tier
1. **Separation of Concerns**: Each tier has single responsibility
2. **Scalability**: Each tier can scale independently
3. **Security**: Database completely isolated from internet
4. **Maintenance**: Easier to update and maintain each tier separately
5. **Cost Optimization**: Can optimize each tier independently
6. **Team Structure**: Clear ownership of each layer

### Benefits Over Two-Tier
- Better security posture (database not exposed)
- Better scalability (don't scale database unnecessarily)
- Better resilience (database issues don't affect frontend)
- Better compliance (PCI-DSS requires network segmentation)

---

## ADR 5: Infrastructure as Code with Terraform

### Context
Need to provision and manage AWS infrastructure.

### Decision
Use Terraform for all infrastructure provisioning.

### Rationale
1. **IaC Best Practices**: Version control, reproducibility, auditability
2. **Multi-Cloud**: Not locked to AWS-only tools (CloudFormation)
3. **Learning**: Terraform skills transfer to other cloud providers
4. **State Management**: Clear understanding of infrastructure state
5. **Team Collaboration**: Easy code review and peer approval

### Terraform File Structure
```
aws/terraform/
├── main.tf              # VPC, networking, security groups
├── beanstalk.tf         # Elastic Beanstalk configuration
├── mongodb.tf           # MongoDB EC2 instance
├── variables.tf         # Input variables
├── terraform.tfvars     # Variable values
├── outputs.tf           # Output values
└── mongodb-install.sh   # MongoDB installation script
```

---

## ADR 6: Auto-Scaling Triggers

### Context
Need to automatically adjust application capacity based on demand.

### Decision
Use CPU Utilization as primary metric for auto-scaling.

### Scaling Rules
- **Scale Up**: CPU > 70% for 2 minutes
- **Scale Down**: CPU < 30% for 2 minutes
- **Min Instances**: 2 (for HA)
- **Max Instances**: 6 (cost control)
- **Cool Down**: 300 seconds (prevent flapping)

### Rationale
1. **CPU Metric**: Simple, reliable, widely understood
2. **Thresholds**: 70%/30% provides good balance
3. **Cool Down**: Prevents rapid scaling changes
4. **Min 2 Instances**: Ensures availability during updates
5. **Max 6 Instances**: Cost control, can adjust based on budget

### Alternative Metrics Considered
- **Request Count**: Would require ALB target tracking (more complex)
- **Custom Metrics**: Would require application instrumentation
- **Network Traffic**: Can be noisy, not reliable

---

## ADR 7: VPC Networking Strategy

### Context
Need to design secure network topology for three-tier application.

### Decision
- Public subnets for ALB
- Private subnets for Beanstalk and MongoDB
- NAT Gateway for outbound internet access from private subnets

### Network Layout
```
VPC: 10.0.0.0/16
├── Public Subnet 1: 10.0.1.0/24 (ALB)
├── Public Subnet 2: 10.0.2.0/24 (ALB)
├── Private Subnet 1: 10.0.10.0/24 (Beanstalk + MongoDB)
└── Private Subnet 2: 10.0.11.0/24 (Beanstalk)

Internet ↔ IGW ↔ Public Subnets (ALB) ↔ NAT ↔ Private Subnets
```

### Benefits
1. **Security**: Database never directly exposed to internet
2. **HA**: Multi-AZ deployment for fault tolerance
3. **Scalability**: Room for growth in subnets
4. **Cost**: NAT Gateway is economical solution

---

## ADR 8: Security Group Rules

### Context
Need to allow only necessary traffic between tiers.

### Decision
Implement restrictive security groups:
- **ALB SG**: Allow 80/443 from internet
- **Beanstalk SG**: Allow 5000 from ALB only
- **MongoDB SG**: Allow 27017 from Beanstalk SG only

### Rationale
1. **Least Privilege**: Only allow necessary traffic
2. **Defense in Depth**: Multiple layers of security
3. **Auditability**: Clear rules for compliance
4. **Performance**: Reduces unnecessary traffic

---

## ADR 9: Environment Variables for Configuration

### Context
Need to manage configuration across different environments.

### Decision
Use environment variables for all sensitive configuration.

### Variables
- `MONGODB_URI`: Database connection string
- `ENVIRONMENT`: Deployment environment (dev/prod)
- `PORT`: Application port
- `FLASK_ENV`: Flask environment mode
- `AWS_REGION`: AWS region

### Rationale
1. **Security**: Secrets never committed to git
2. **Flexibility**: Easy to change per environment
3. **Standards**: 12-factor app methodology
4. **CI/CD**: Easy to set in build pipeline

---

## ADR 10: Monitoring and Logging Strategy

### Context
Need visibility into application and infrastructure health.

### Decision
Use CloudWatch for centralized monitoring and logging.

### Implementation
- **Application Logs**: Captured from Beanstalk instances
- **Infrastructure Metrics**: CPU, Memory, Disk from EC2
- **Alarms**: Auto-triggered for CPU > 80%, Storage > 85%
- **Dashboards**: Visual monitoring of key metrics

### Rationale
1. **Centralized**: Single pane of glass for all monitoring
2. **AWS Native**: No additional tools required
3. **Cost-Effective**: Included in AWS services
4. **Integration**: Works with SNS for notifications

