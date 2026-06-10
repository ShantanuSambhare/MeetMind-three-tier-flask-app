# MongoDB EC2 Instance (Tier 3 - Private Subnet)

# Get latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# MongoDB EC2 Instance
resource "aws_instance" "mongodb" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.mongodb_instance_type
  subnet_id              = aws_subnet.private_1.id
  vpc_security_group_ids = [aws_security_group.mongodb.id]
  
  # EBS volume for MongoDB data
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 100
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "meetmind-mongodb-root"
    }
  }

  # MongoDB data volume
  ebs_block_device {
    device_name           = "/dev/sdf"
    volume_type           = "gp3"
    volume_size           = 200
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "meetmind-mongodb-data"
    }
  }

  # User data to install MongoDB
  user_data = base64encode(templatefile("${path.module}/mongodb-install.sh", {
    mongodb_password = var.mongodb_root_password
  }))

  monitoring = true

  tags = {
    Name = "meetmind-mongodb"
  }

  lifecycle {
    ignore_changes = [ami]
  }
}

# Elastic IP for MongoDB (optional, for accessing via SSM Session Manager)
resource "aws_eip" "mongodb_management" {
  instance = aws_instance.mongodb.id
  domain   = "vpc"

  tags = {
    Name = "meetmind-mongodb-eip"
  }

  depends_on = [aws_internet_gateway.main]
}

# CloudWatch alarms for MongoDB
resource "aws_cloudwatch_metric_alarm" "mongodb_cpu" {
  alarm_name          = "meetmind-mongodb-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Alert when MongoDB CPU exceeds 80%"

  dimensions = {
    InstanceId = aws_instance.mongodb.id
  }
}

resource "aws_cloudwatch_metric_alarm" "mongodb_storage" {
  alarm_name          = "meetmind-mongodb-storage"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "DiskSpaceUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "Alert when MongoDB storage exceeds 85%"

  dimensions = {
    InstanceId = aws_instance.mongodb.id
  }
}

# Output MongoDB connection details
output "mongodb_private_ip" {
  value       = aws_instance.mongodb.private_ip
  description = "Private IP of MongoDB instance"
}

output "mongodb_connection_string" {
  value       = "mongodb://admin:${var.mongodb_root_password}@${aws_instance.mongodb.private_ip}:27017/meetmind?authSource=admin"
  description = "MongoDB connection string"
  sensitive   = true
}
