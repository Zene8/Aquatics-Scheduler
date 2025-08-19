# Streamlit Deployment Guide

## Firebase Credentials Setup

To deploy this app to Streamlit Cloud, you need to configure Firebase credentials using Streamlit secrets.

### Step 1: Create Streamlit Secrets

1. Go to your Streamlit Cloud dashboard
2. Navigate to your app settings
3. Click on "Secrets" in the sidebar
4. Add the following configuration:

```toml
[firebase]
type = "service_account"
project_id = "aqua-scheduler-pro"
private_key_id = "2dce826c9a84f066ef200aa2363c2c1361293ee9"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC0S/824emRb5is\nlfkUQe8+lNUitVGU+VQiR/Z4QgXg/qYRNS4eIUl0VC3nuvlphiGAy87BP89SqNNS\nubZ+faVD0czwoozx7OGoPFY4nKy56peLnz0KxvctsTiLZMkfWYaGpWzP7HLxGYC/\n5bAdErBZeUN4djtXrUh3Cc3P9NKDR3r4+xisK8XipARaiRKlQae4+L4V2tx4c8eo\nm2JEqPBwJDM9Btffyv4uHj1qUGSvD3sq5mu1R6NntgQtNjGYLwe2uDqvInbjZG64\n/3J5HBZ/NViCuTWkh3Y3rT2OIscqNQsF4eMHvRLAwgYDQFFLc6dJoseEjnbf200X\nw82uKJzXAgMBAAECggEADsrhcJ5ObIlMbHSNkBTszSSm7AcWX3OpbHqdBTbdhp0+\nANFtLDms7idt8MJNblP78bZHC2Hx36VMWVA1YeFrKspO1ztu9vZpeUUiCdkI7uQJ\ndQImnvi+FPiiXAVz3ueYevmdmN2cfJ2MC7KLpYcAAwdI+twweDwWYvXh9frvPqf+\nTSZaQ0NQOvxYKTX2VMxea0GdLgWjd+Q+5BCqIGpch0aLK+xT3qNRXo9ipy2atWbN\nYwfjbu+jraOBPegxGflkrLnZrbsi1NYvfFsrTFo5clr0eobrBcZbjVZ5kQ/Zn0HX\nE+yJ9BqMwnRqrvz5iwOWrh94nHBCMX2xjXNvmlkS4QKBgQDr/iiZD/9fEVWnxksJ\nTejBbNacgNMreYJqlrSZqnVkWMAVgvjY9LoNFyL/5/ACkwL9/q5ISOl9hIiwZar0\n+d00BxOToTAOk2R0z9ADJnrMhdd//KAmwyiGEiVpxpXTsNzAiIiIzmpKtpPWP6u2\nw02nTKDmPQ4EIfvTs79ksCNm0QKBgQDDlQxTQXLXWpYmnDwnZQaSPFM+f7WWjAaD\nST7mo/xepBNlQz5UebKHyCaOLoXPbBrUZw1o8Uq9zFzxcd9dFKevTmXuQGwq5Yrv\nXP1dihIuqnUWZOUKqF0Eoiw61HsQjwh699IZA9VJlj2/n2m6q1N7dIyg9lUj9XB+\nJRO88HeDJwKBgQCoVddntz2V9qt+zbdgn65Tqus7H7mB3V7l4TJaGnk6ZwQ9U/tl\n5st/4u0YVb2iWHNd8nknHrtOyWcnTJ4xuLnNDu8r82JwQzr5B/N9C8m0chRSO0WR\n4MvbNr5xQTJGmnYc8EdULskrGilCPpCiAZY2rDZphUumLweO7zyq+emGwQKBgHzU\nk9JLsqW6/pzUGRy3wVLyx9rbHiZhZwLCbDA/OCObq3l1SsIWDpnVaK5VCTjTcehh\ngdCaOS8c0bGVEZBST5h3fF1tptxWN7AA9QGPz30TdLn/WaTMwtnjPEGsPoPaFvqN\nU/59UNOv3eeBMrVfBmCEigFuV/ckf1E0Dv4HqO//AoGBAIeu6E9K+5tSzQfPmhUa\nw6zI5nE70GKP0WSgzNx+7se+uIpXFG3UZOFGixvkEZaWnvza66Fd2VuiDiyUS1Ok\nqSayYKGUg1DVPbaph38Bk9fiKJvkoTGRjQIUHQb5YEfAcUDX8BFpRCHUSx4uwMix\nv/yUC3LBKlwR2TUyBQ67TaZc\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-fbsvc@aqua-scheduler-pro.iam.gserviceaccount.com"
client_id = "100230033327803685875"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40aqua-scheduler-pro.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

### Step 2: Deploy to Streamlit

1. Push your code to GitHub
2. Connect your GitHub repository to Streamlit Cloud
3. Deploy the app

### Step 3: Verify Deployment

The app should now work correctly with Firebase authentication and database operations.

## Local Development

For local development, the app will automatically use the `serviceAccountKey.json` file in the project directory.

## Troubleshooting

### "Invalid database URL: None" Error
- Ensure Firebase credentials are properly configured in Streamlit secrets
- Check that the `databaseURL` is included in the Firebase configuration

### "Invalid JWT Signature" Error
- This may be due to time synchronization issues or service account key problems
- The app will continue to work but may show a warning

### "serviceAccountKey.json not found" Error
- For local development: Ensure the file is in the project directory
- For deployment: Ensure Firebase credentials are in Streamlit secrets

## Security Notes

- Never commit `serviceAccountKey.json` to version control
- Use Streamlit secrets for deployment
- Keep your Firebase project secure
