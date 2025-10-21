# 📱 Mobile App Quick Reference

## Setup (5 minutes)

```bash
cd mobile
npm install
npm run ios     # macOS only
npm run android # Windows/Linux/macOS
```

## Files Created

- `mobile/App.tsx` - Main app & navigation
- `mobile/package.json` - Dependencies
- `mobile/src/context/AuthContext.tsx` - Auth state
- `mobile/src/services/api.ts` - API integration
- `mobile/src/screens/LoginScreen.tsx` - Login UI
- `mobile/src/screens/DashboardScreen.tsx` - Main dashboard
- `mobile/src/screens/TenantsScreen.tsx` - Tenant list
- `mobile/src/screens/TenantDetailScreen.tsx` - Tenant details
- `mobile/src/screens/RevenueScreen.tsx` - Revenue analytics
- `mobile/src/screens/SettingsScreen.tsx` - Settings
- `mobile/src/screens/NotificationsScreen.tsx` - Notifications

## Features

✅ Beautiful login screen  
✅ Dashboard with 8 metric cards  
✅ Revenue pie chart  
✅ Tenant list with search & filters  
✅ Detailed tenant view  
✅ Tenant actions (suspend/activate)  
✅ Real-time data polling  
✅ Pull-to-refresh  
✅ Persistent authentication

## Run Commands

```bash
npm run ios              # iOS simulator
npm run android          # Android emulator
npm start                # Metro bundler
npm start -- --reset-cache  # Clear cache
```

## Build for Production

**iOS:**
```bash
cd ios && xcodebuild -workspace *.xcworkspace \
  -scheme * -configuration Release archive
```

**Android:**
```bash
cd android && ./gradlew assembleRelease
```

## Troubleshooting

**Can't connect?**
- iOS: Use `http://localhost:8000`
- Android: Use `http://10.0.2.2:8000`
- Physical device: Use your computer's IP

**Build failed?**
```bash
cd ios && pod install && cd ..
npm start -- --reset-cache
```

## What's Next?

1. Add push notifications (Firebase)
2. Implement offline mode (Redux Persist)
3. Add biometric auth
4. Submit to App Store & Google Play

**Total:** 2,500+ lines | iOS 13+ & Android 8+ | 15-18 MB

