%define _version 2.0.2
%define _release 1

Name:           sw
Version:        %{_version}
Release:        %{_release}%{?dist}
Summary:        An overly complicated wallpaper switcher for Hyprland
License:        MIT
URL:            https://github.com/AntonVanAssche/sw

Source0:        %{name}-%{_version}.tar.gz
Source1:        %{name}
Source2:        %{name}-daemon

BuildRequires:  python3-devel
Requires:       python3

%description
Manage your wallpapers on Hyprland with sw, an overly complicated yet powerful wallpaper
switcher and manager. It supports advanced features like wallpaper queues, history tracking,
and integration with systemd timers to automate wallpaper changes seamlessly.
Perfect for users who want fine-grained control over their Hyprland desktop backgrounds.

%define _buildshell /usr/bin/bash
%define __python    /usr/bin/python3
%define python3_version 3.13
%global __requires_exclude_from ^/usr/local/lib/%{name}/.*\\.so.*$

%prep
%{__python} -m venv --clear ./%{name}


%build
. ./%{name}/bin/activate
python -m pip install --disable-pip-version-check --no-cache-dir --no-compile %{SOURCE0}
deactivate
find ./%{name} -type d -name __pycache__ -exec rm -rf '{}' '+'
find ./%{name} -type f -exec %{__sed} -i 's|%{_builddir}|/usr/local/lib|g' '{}' '+'

%install
%{__mkdir_p} %{buildroot}/usr/local/lib
%{__cp} -r ./%{name} %{buildroot}/usr/local/lib
%{__mkdir_p} %{buildroot}/usr/local/bin
%{__ln_s} /usr/local/lib/%{name}/bin/%{name} %{buildroot}/usr/local/bin/%{name}
%{__ln_s} /usr/local/lib/%{name}/bin/%{name}-daemon %{buildroot}/usr/local/bin/%{name}-daemon
%{py3_shebang_fix} %{buildroot}/usr/local/lib/%{name} &>/dev/null

%files
%defattr(-,root,root,-)
/usr/local/bin/%{name}
/usr/local/lib/%{name}
/usr/local/bin/%{name}-daemon
