from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from .models import Exhibition, Category, Material, Piece, Comment, GuestBook, ExhibitionLike, PieceLike, \
    ExhibitionClick, PieceClick, ExhibitionShare, PieceShare
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q


class CommentManage:
    def create_comment(request, pk):
        if request.user.is_authenticated:
            piece = get_object_or_404(Piece, pk=pk)

            if request.method == 'POST':
                comment = Comment(content=request.POST.get('content'), piece=piece, user=request.user)
                comment.save()
                messages.info(request, "댓글이 등록되었습니다.")
                return redirect(comment.get_absolute_url())
            else:
                return redirect(piece.get_absolute_url())
        else:
            return PermissionDenied

    def delete_comment(request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        piece = comment.piece
        if request.user.is_authenticated and request.user == comment.user:
            comment.delete()
            messages.info(request, "댓글이 삭제되었습니다.")
            return redirect(piece.get_absolute_url())
        else:
            raise PermissionDenied


class GuestbookManage:
    def create_guestbook(request, pk):
        if request.user.is_authenticated:
            exhibition = get_object_or_404(Exhibition, pk=pk)

            if request.method == 'POST':
                guestbook = GuestBook(content=request.POST.get('content'), exhibition=exhibition, user=request.user)
                guestbook.save()
                messages.info(request, "방명록이 등록되었습니다.")
                return redirect(guestbook.get_absolute_url())
            else:
                return redirect(exhibition.get_absolute_url())
        else:
            return PermissionDenied

    def delete_guestbook(request, pk):
        guestbook = get_object_or_404(GuestBook, pk=pk)
        exhibition = guestbook.exhibition
        if request.user.is_authenticated and request.user == guestbook.user:
            guestbook.delete()
            messages.info(request, "방명록이 삭제되었습니다.")
            return redirect(exhibition.get_absolute_url())
        else:
            raise PermissionDenied


class LikeManage:
    def exhibition_like(request, pk):
        if request.user.is_authenticated:
            exhibition = get_object_or_404(Exhibition, pk=pk)
            older_like = ExhibitionLike.objects.filter(exhibition=exhibition, user=request.user)

            if older_like:
                return redirect(exhibition.get_absolute_url())

            like = ExhibitionLike(exhibition=exhibition, user=request.user)
            like.save()
            return redirect(like.get_absolute_url())
        else:
            return PermissionDenied

    def exhibition_dislike(request, ak, pk):
        like = get_object_or_404(ExhibitionLike, pk=pk)
        exhibition = like.exhibition
        if request.user.is_authenticated and request.user == like.user:
            like.delete()
            return redirect(exhibition.get_absolute_url())
        else:
            return PermissionDenied

    def piece_like(request, pk):
        if request.user.is_authenticated:
            piece = get_object_or_404(Piece, pk=pk)
            older_like = PieceLike.objects.filter(piece=piece, user=request.user)
            if older_like:
                return redirect(piece.get_absolute_url())

            like = PieceLike(piece=piece, user=request.user)
            like.save()
            return redirect(like.get_absolute_url())
        else:
            return PermissionDenied

    def piece_dislike(request, ak, pk):
        like = get_object_or_404(PieceLike, pk=pk)
        if request.user.is_authenticated and like.user == request.user:
            like.delete()
            return redirect(like.get_absolute_url())
        else:
            return PermissionDenied


class LikePieceList(ListView):
    model = PieceLike
    template_name = 'exhibition/common/preference.html'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        piece_like_list = PieceLike.objects.filter(user=user).order_by('pk')
        return piece_like_list

    def get_context_data(self, **kwargs):
        context = super(LikePieceList, self).get_context_data()
        context['mode'] = '작품'
        return context


class LikeExhibitionList(ListView):
    model = ExhibitionLike
    template_name = 'exhibition/common/preference.html'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        exhibition_like_list = ExhibitionLike.objects.filter(user=user).order_by('pk')
        return exhibition_like_list

    def get_context_data(self, **kwargs):
        context = super(LikeExhibitionList, self).get_context_data()
        context['mode'] = '전시회'
        return context


class ExhibitionSearch(ListView):
    model = Exhibition
    template_name = 'exhibition/common/search_result.html'
    paginate_by = 8

    def get_queryset(self):
        q = self.kwargs['q']
        piece_list = Exhibition.objects.filter(
            Q(name__contains=q) | Q(explain__contains=q)).distinct()
        return piece_list

    def get_context_data(self, **kwargs):
        context = super(ExhibitionSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'{q}'
        return context


class PieceSearch(ListView):
    model = Piece
    template_name = 'exhibition/common/search_result.html'
    paginate_by = 8

    def get_queryset(self):
        q = self.kwargs['q']
        piece_list = Piece.objects.filter(
            Q(name__contains=q) | Q(author__contains=q) | Q(material__name__contains=q)).distinct()
        return piece_list

    def get_context_data(self, **kwargs):
        context = super(PieceSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'{q}'
        return context


class CategoryManage:
    def category_page(request, slug):
        category = Category.objects.get(slug=slug)

        return render(
            request,
            'exhibition/user/user_exhibition_list.html',
            {
                'exhibition_list': Exhibition.objects.filter(category=category),
                'categories': Category.objects.all(),
                'category_name': category,
            }
        )


class MaterialManage:
    def meterial_page(request, slug):
        material = Material.objects.get(slug=slug)

        return render(
            request,
            'exhibition/user/user_exhibition_detail.html',
            {
                'piece_list': Piece.objects.filter(material=material),
                'materials': Material.objects.all(),
                'material_name': material,
            }
        )


class ShareManage:
    def exhibition_share(request, pk):
        if request.user.is_authenticated:
            exhibition = get_object_or_404(Exhibition, pk=pk)
            share = ExhibitionShare(exhibition=exhibition, user=request.user)
            share.save()
            return redirect(exhibition.get_absolute_url())
        else:
            return PermissionDenied

    def piece_share(request, pk):
        if request.user.is_authenticated:
            piece = get_object_or_404(Piece, pk=pk)
            share = PieceShare(piece=piece, user=request.user)
            share.save()
            return redirect(piece.get_absolute_url())
        else:
            return PermissionDenied
